import { fastify, FastifyRequest, FastifyReply, FastifyError } from 'fastify'
import { Server, IncomingMessage } from 'http'
import { v4 as uuidv4, version as uuidVersion, validate as uuidValidate } from 'uuid'
import { REST } from '@discordjs/rest'
import { Routes } from 'discord-api-types/v9'
import { Client as DiscordClient, Intents, CommandInteraction } from 'discord.js'
import { SlashCommandBuilder } from '@discordjs/builders'
import { parse as parseCookies } from 'cookie'

const APP_PROTOCOL = process.env.APP_PROTOCOL || 'http'
const APP_HOSTNAME = process.env.APP_HOSTNAME || 'localhost'
const APP_URL = `${APP_PROTOCOL}://${APP_HOSTNAME}`

const ADMIN_SECRET = process.env.ADMIN_SECRET || 'superSecretCookie'
const FLAG = process.env.FLAG || 'buckeye{fake_flag}'

const DISCORD_TOKEN = process.env.APP_DISCORD_TOKEN!
const CLIENT_ID = process.env.APP_CLIENT_ID!

const server = fastify({
  logger: {
    level: process.env.NODE_ENV === 'production' ? 'info' : 'debug'
  }
})

const discordClient = new DiscordClient({
  intents: [
    Intents.FLAGS.GUILDS,
    Intents.FLAGS.GUILD_MEMBERS,
    Intents.FLAGS.DIRECT_MESSAGES
  ]
})

const db: { [key: string]: string; } = {}

// ---

interface ICanaryParams { token: string; }

type HookHandlerDoneFunction = <TError extends Error = FastifyError>(err?: TError) => void

function validateToken (
  request: FastifyRequest<{ Params: ICanaryParams; }, Server, IncomingMessage>,
  reply: FastifyReply<Server, IncomingMessage>,
  done: HookHandlerDoneFunction
) {
  const token = request.params.token
  if (uuidValidate(token) && uuidVersion(token) === 4 && token in db) {
    done()
  } else {
    reply.code(400)
    done(new Error('Bad token'))
  }
}

async function notifyUser (
  request: FastifyRequest<{ Params: ICanaryParams; }, Server, IncomingMessage>
) {
  const token = request.params.token
  const userTag = db[token]
  const user = await discordClient.users.fetch(userTag)
  const tagline = `:warning: **ALERT** \`${request.url}\` was triggered by **${request.ip}**\n`
  const headers =
    '```' +
    Object.keys(request.headers)
      .map(name => `${name}: ${request.headers[name]}`)
      .join('\n') +
    '```'

  const msg = `${tagline}${headers}`
  await user.send(msg)
}

server.get<{Params: ICanaryParams}>(
  '/canary/:token',
  { preValidation: validateToken },
  async (request, reply) => {
    notifyUser(request)
    await reply.send('Ok buddy')
  }
)

server.get<{Params: ICanaryParams}>(
  '/canary/:token/*',
  { preValidation: validateToken },
  async (request, reply) => {
    notifyUser(request)
    await reply.send('Ok buddy')
  }
)

server.get(
  '/flag',
  async (request, reply) => {
    if (request.headers.cookie !== undefined) {
      const cookies = parseCookies(request.headers.cookie)
      if (cookies.auth === ADMIN_SECRET) {
        await reply.send(FLAG)
        return
      }
    }

    await reply.code(403).send(new Error("You're not the admin"))
  }
)

server.listen(8080, '0.0.0.0', (error, address) => {
  if (error) { throw error }
  console.log(`Server listening at ${address}`)
});

// ---

(async () => {
  const deleteCommand = new SlashCommandBuilder()
    .setName('delete')
    .setDescription('Delete a canary URL')
    .addStringOption(option =>
      option.setName('url')
        .setDescription('The canary URL to delete')
        .setRequired(true)
    )

  const createCommand = new SlashCommandBuilder()
    .setName('create')
    .setDescription('Create a new canary URL')

  const infoCommand = new SlashCommandBuilder()
    .setName('info')
    .setDescription('Bot info')

  const commands = [
    deleteCommand.toJSON(),
    createCommand.toJSON(),
    infoCommand.toJSON()
  ]
  const rest = new REST({ version: '9' }).setToken(DISCORD_TOKEN)

  console.log('Started refreshing application (/) commands.')

  await rest.put(
    Routes.applicationCommands(CLIENT_ID),
    { body: commands }
  )

  console.log('Successfully reloaded application (/) commands.')
})()

discordClient.on('ready', () => {
  console.log(`Logged in as ${discordClient.user!.tag}!`)
  discordClient.user!.setPresence({
    activities: [{ name: 'DM me' }]
  })
})

async function commandCreate (interaction: CommandInteraction) {
  const token = uuidv4()
  db[token] = interaction.user.id

  await interaction.reply({
    content: `Here you go: <${APP_URL}/canary/${token}>
If anyone sends a request to that URL, I will DM you`,
    ephemeral: true
  })
}

async function commandDelete (interaction: CommandInteraction) {
  try {
    const url = new URL(interaction.options.getString('url')!)
    const prefix = '/canary/'
    if (!url.pathname.startsWith(prefix)) {
      throw new Error('Not a canary URL')
    }

    const token = url.pathname.split('/')[2]
    if (token in db) {
      delete db[token]
      await interaction.reply({
        content: 'Deleted :ok_hand:',
        ephemeral: true
      })
    } else {
      throw new Error("That canary URL doesn't even exist")
    }
  } catch (e) {
    await interaction.reply({
      content: `:x: \`${e}\``,
      ephemeral: true
    })
  }
}

discordClient.on('interactionCreate', async (interaction) => {
  if (!interaction.isCommand()) return
  switch (interaction.commandName) {
    case 'create':
      await commandCreate(interaction)
      break
    case 'delete':
      await commandDelete(interaction)
      break
    case 'info':
      await interaction.reply('Source code: http://github.com/qxxxb/canary')
      break
  }
})

discordClient.login(DISCORD_TOKEN)
