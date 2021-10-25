import { REST } from '@discordjs/rest'
import { Routes } from 'discord-api-types/v9'
import { Client, Intents, CommandInteraction } from 'discord.js'
import { SlashCommandBuilder } from '@discordjs/builders'
import path from 'path'
import fs from 'fs'
import { spawnSync } from 'child_process'
import crypto from 'crypto'
import pino from 'pino'

const DISCORD_TOKEN = process.env.DISCORD_TOKEN!
const CLIENT_ID = process.env.CLIENT_ID!
const FLAG = process.env.FLAG!

const TMP_DIR = '/tmp/images/'
if (!fs.existsSync(TMP_DIR)) {
  fs.mkdirSync(TMP_DIR)
}

const logger = pino(pino.destination('app.log'))

const client = new Client({
  intents: [
    Intents.FLAGS.GUILDS,
    Intents.FLAGS.DIRECT_MESSAGES
  ]
});

(async () => {
  const embedCommand = new SlashCommandBuilder()
    .setName('embed')
    .setDescription('Embed a secret message in an image')
    .addStringOption(option =>
      option.setName('image_url')
        .setDescription('Image URL')
        .setRequired(true)
    )
    .addStringOption(option =>
      option.setName('message')
        .setDescription('The message to embed')
        .setRequired(false)
    )
    .addStringOption(option =>
      option.setName('password')
        .setDescription('The password used to encrypt the message')
        .setRequired(false)
    )

  const extractCommand = new SlashCommandBuilder()
    .setName('extract')
    .setDescription('Extract a secret message from an image')
    .addStringOption(option =>
      option.setName('image_url')
        .setDescription('Image URL')
        .setRequired(true)
    )
    .addStringOption(option =>
      option.setName('password')
        .setDescription('The password used to decrypt the message')
        .setRequired(true)
    )

  const infoCommand = new SlashCommandBuilder()
    .setName('info')
    .setDescription('Bot info')

  const commands = [
    embedCommand.toJSON(),
    extractCommand.toJSON(),
    infoCommand.toJSON()
  ]
  const rest = new REST({ version: '9' }).setToken(DISCORD_TOKEN)

  console.log('Started refreshing application (/) commands.')

  if (process.env.NODE_ENV === 'production') {
    await rest.put(
      Routes.applicationCommands(CLIENT_ID),
      { body: commands }
    )
  } else {
    // Guild commands refresh a lot faster than global commands. Good for
    // development
    const GUILD_ID = process.env.GUILD_ID!
    await rest.put(
      Routes.applicationGuildCommands(CLIENT_ID, GUILD_ID),
      { body: commands }
    )
  }

  console.log('Successfully reloaded application (/) commands.')
})()

client.on('ready', () => {
  console.log(`Logged in as ${client.user!.tag}!`)
  client.user!.setPresence({
    activities: [{ name: 'DM me' }]
  })
})

function downloadFile (url: string, output: string) {
  const result = spawnSync(
    'curl',
    [url, '-o', output, '--max-filesize', '8388608'],
    { timeout: 5000 }
  )
  if (result.error) { throw result.error }
  if (!fs.existsSync(output)) { throw new Error('Failed to download file') }
  return result
}

function randomString (): string {
  return crypto.randomBytes(16).toString('hex')
}

function stegEmbed (imagePath: string, message: string, password: string): string {
  const messagePath = path.join(TMP_DIR, randomString())
  fs.writeFileSync(messagePath, message)

  const outputPath = path.join(TMP_DIR, `${randomString()}.jpg`)

  spawnSync(
    'steghide',
    [
      'embed',
      '--embedfile', messagePath,
      '--coverfile', imagePath,
      '--stegofile', outputPath,
      '--passphrase', password,
      '--force', '--quiet'
    ],
    { timeout: 1000 }
  )

  fs.unlinkSync(messagePath)

  if (!fs.existsSync(outputPath)) { throw new Error('Failed to embed message') }

  logger.info({ imagePath, outputPath, password })
  return outputPath
}

function stegExtract (imagePath: string, password: string): string {
  const messagePath = path.join(TMP_DIR, crypto.randomBytes(16).toString('hex'))

  spawnSync(
    'steghide',
    [
      'extract',
      '--stegofile', imagePath,
      '--passphrase', password,
      '--extractfile', messagePath,
      '--force', '--quiet'
    ],
    { timeout: 1000 }
  )

  fs.unlinkSync(imagePath)
  if (!fs.existsSync(messagePath)) {
    throw new Error('Failed to extract message')
  }

  const result = fs.readFileSync(messagePath).toString()
  fs.unlinkSync(messagePath)
  return result
}

async function commandEmbed (interaction: CommandInteraction) {
  const imageURL = interaction.options.getString('image_url')!
  const imagePath = path.join(TMP_DIR, `${randomString()}.jpg`)
  downloadFile(imageURL, imagePath)

  const message = interaction.options.getString('message')
  const password = interaction.options.getString('password')

  if (!message) {
    await interaction.reply({
      content: "No message provided, so here's the blank image",
      files: [imagePath],
      ephemeral: true
    })
    return
  }

  if (!password) { throw new Error('A password is required!') }

  const outputPath = stegEmbed(imagePath, message, password)
  await interaction.reply({
    content: 'Done',
    files: [outputPath],
    ephemeral: true
  })
}

async function commandExtract (interaction: CommandInteraction) {
  const imageURL = interaction.options.getString('image_url')!
  const imagePath = path.join(TMP_DIR, `${randomString()}.jpg`)
  downloadFile(imageURL, imagePath)

  const password = interaction.options.getString('password')!
  const message = stegExtract(imagePath, password)

  await interaction.reply({
    content: `Here's the message: ${message}`,
    ephemeral: true
  })
}

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isCommand()) return

  try {
    switch (interaction.commandName) {
      case 'embed':
        return await commandEmbed(interaction)
      case 'extract':
        return await commandExtract(interaction)
      case 'info':
        return await interaction.reply('Source code: http://github.com/qxxxb/StegBot')
    }
  } catch (error) {
    await interaction.reply({
      content: `:x: ${error}`,
      ephemeral: true
    })
  }
})

stegEmbed('bof.jpg', FLAG, randomString())
client.login(DISCORD_TOKEN)
