import { Client, Intents } from 'discord.js'
import axios from 'axios'
import { wrapper } from 'axios-cookiejar-support'
import { Cookie, CookieJar, MemoryCookieStore } from 'tough-cookie'

const APP_HOSTNAME = process.env.APP_HOSTNAME || 'localhost'
const ADMIN_SECRET = process.env.ADMIN_SECRET || 'superSecretCookie'
const DISCORD_TOKEN = process.env.ADMIN_DISCORD_TOKEN!

const client = new Client({
  intents: [Intents.FLAGS.DIRECT_MESSAGES],
  partials: ['CHANNEL']
})

client.on('ready', () => {
  console.log(`Logged in as ${client.user!.tag}!`)
  client.user!.setPresence({
    activities: [{ name: 'DM me' }]
  })
})

client.on('messageCreate', async (message) => {
  if (message.author.bot) return

  if (
    !(
      message.content.startsWith('http://') ||
      message.content.startsWith('https://')
    )
  ) {
    message.channel.send("I'm just a bot. Maybe send me a URL and I'll open it")
    return
  }

  try {
    if (
      message.content.startsWith(`http://${APP_HOSTNAME}`) ||
      message.content.startsWith(`https://${APP_HOSTNAME}`)
    ) {
      message.channel.send("I see you're trying to steal my cookie :rage:")
      return
    }

    message.channel.sendTyping()

    const jar = new CookieJar(
      new MemoryCookieStore(),
      { allowSpecialUseDomain: true }
    )
    const cookie = new Cookie({
      key: 'auth',
      value: ADMIN_SECRET,
      domain: APP_HOSTNAME
    })

    jar.setCookieSync(cookie, `https://${APP_HOSTNAME}`)

    const client = wrapper(axios.create({ jar }))
    const response = await client.get(message.content, { maxRedirects: 0 })

    await message.channel.send(
      `I fetched your URL and got a ${response.status} status code`
    )
  } catch (e) {
    message.channel.send(`:x: \`${e}\``)
  }
})

client.login(DISCORD_TOKEN)
