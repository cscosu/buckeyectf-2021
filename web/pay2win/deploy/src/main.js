/* global swal */
import devtools from 'devtools-detect'

const overlayMask = document.querySelector('#overlay-mask')
const popups = document.querySelectorAll('.popup')

const cookieMessage = document.querySelector('#cookie-message')
const notifPermissionFake = document.querySelector('#notif-permission-fake')
const notifPermissionReal = document.querySelector('#notif-permission-real')
const subscribe = document.querySelector('#subscribe')
const membership = document.querySelector('#membership')
const continueReading = document.querySelector('#continue-reading')

const subscribeNewsletterAlert = {
  title: 'Subscribe to our Newsletter!',
  text: 'Please enter your email address',
  content: subscribe,
  buttons: ['OK', 'No thanks']
}

const adblockAlert = {
  title: 'Adblock detected',
  text: 'Please disable your adblocker',
  icon: 'error'
}

const scrollAlert = {
  icon: 'info',
  title: 'You scrolled!',
  text: "Seems like you're interested in our content! Now please subscribe to our newsletter:",
  content: subscribe,
  buttons: ['OK', 'No thanks']
}

const flagAlert = {
  icon: 'error',
  title: 'The flag is only available to paying members!',
  text: 'Enter your email address to sign up:',
  content: subscribe,
  buttons: ['OK', 'No thanks']
}

const luckyAlert = {
  icon: 'success',
  title: 'You are the 5,000,000th visitor on this website!',
  text: 'Claim your $1,000 cash award NOW!',
  content: subscribe,
  buttons: ['Yes please', 'No thanks']
}

const devtoolsAlert = {
  icon: 'error',
  title: 'Trying to open DevTools?',
  text: "Well that's not allowed.",
  button: "Sorry I'll leave now",
  closeOnClickOutside: false,
  closeOnEsc: false
}

function closePopup (popup) {
  overlayMask.classList.remove('active')
  popup.classList.remove('active')
  document.body.classList.remove('no-scroll')
}

function openPopup (popup) {
  popup.classList.add('active')
  overlayMask.classList.add('active')
  document.body.classList.add('no-scroll')
}

let alerting = false

async function doAlert (config, force = false) {
  if (!alerting || force) {
    alerting = true
    document.body.classList.add('no-scroll')
    await swal(config)
    document.body.classList.remove('no-scroll')
    alerting = false
  }
}

const closeEvent = new Event('close')

for (const popup of popups) {
  const closers = popup.querySelectorAll('.close')
  for (const closer of closers) {
    closer.addEventListener('click', (event) => {
      closePopup(popup)
      popup.dispatchEvent(closeEvent)
    })
  }
}

function welcomeSequence () {
  openPopup(cookieMessage)

  cookieMessage.addEventListener('close', (event) => {
    openPopup(notifPermissionFake)
  })

  notifPermissionFake.addEventListener('close', (event) => {
    openPopup(notifPermissionReal)
  })

  notifPermissionReal.addEventListener('close', async (event) => {
    await doAlert(subscribeNewsletterAlert)
    await doAlert(adblockAlert)
    openPopup(membership)
  })

  membership.addEventListener('close', (event) => {
    openPopup(continueReading)
    setTimeout(welcomeSequence, 4000)
  })
}

async function beLucky () {
  await doAlert(luckyAlert)
  setTimeout(beLucky, 10000)
}

function addScrollListener () {
  window.addEventListener('scroll', async function scrollListener (event) {
    await doAlert(scrollAlert)
    window.removeEventListener('scroll', scrollListener)
    setTimeout(addScrollListener, 500)
  })
}

async function devToolsOpen (event) {
  setTimeout(
    () => {
      window.location.href = 'https://youtu.be/dQw4w9WgXcQ'
    },
    2000
  )

  await doAlert(devtoolsAlert, true)
}

function addFocusListener () {
  if (devtools.isOpen) {
    devToolsOpen()
  }
  window.addEventListener('focus', async function scrollListener (event) {
    if (devtools.isOpen) {
      devToolsOpen(null)
    }
  })
}

function plantFlag () {
  const ciphertext = [234, 240, 234, 252, 214, 236, 140, 247, 173, 191, 158, 132, 56, 4, 32, 73, 235, 193, 233, 152, 125, 19, 19, 237, 186, 131, 98, 52, 186, 143, 127, 43, 226, 233, 126, 15, 225, 171, 85, 55, 173, 123, 21, 147, 97, 21, 237, 11, 254, 129, 2, 131, 101, 63, 149, 61]
  const plaintext = ciphertext.map((x, i) => ((i * i) % 256) ^ x ^ 0x99)

  const flagElement = document.querySelector('#flag')
  plaintext.map((x, i) => {
    const span = document.createElement('span')
    span.classList.add(`flag-char-${i}`)
    span.textContent = String.fromCharCode(x)
    flagElement.appendChild(span)
    return span
  })

  const flagOverlay = document.querySelector('#flag-overlay')
  flagOverlay.addEventListener('mouseover', async () => {
    await swal(flagAlert)
  })
}

function spamConsole () {
  const randomColor = Math.floor(Math.random() * 16777215).toString(16)
  console.log(
    '%c                                                                ',
    `background: #${randomColor}`
  )
  setTimeout(spamConsole, 100)
}

const hostname = document.querySelector('#hostname')
hostname.textContent = window.location.href

welcomeSequence()
setTimeout(addScrollListener, 1000)
setTimeout(addFocusListener, 3000)
setTimeout(beLucky, 2000)

plantFlag()

spamConsole()
window.addEventListener('devtoolschange', devToolsOpen)
