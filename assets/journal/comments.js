(() => {
  const section = document.querySelector('[data-comment-thread]')
  if (!section || section.dataset.commentStatus !== 'open') return
  const post = section.dataset.commentThread.replace(/^journal:/, '')
  const endpoint = 'https://pgqaqqliefpofsktjhjq.supabase.co/functions/v1/blog-comments'
  const list = section.querySelector('[data-comment-list]')
  const form = section.querySelector('form')
  const status = section.querySelector('[data-comment-feedback]')
  const submit = form.querySelector('button[type="submit"]')

  const render = (comments) => {
    list.replaceChildren()
    for (const item of comments) {
      const article = document.createElement('article')
      const heading = document.createElement('h3')
      heading.textContent = item.display_name
      const body = document.createElement('p')
      body.textContent = item.body
      article.append(heading, body)
      list.append(article)
    }
    if (!comments.length) list.textContent = 'No approved comments yet.'
  }

  fetch(`${endpoint}?post=${encodeURIComponent(post)}`)
    .then((response) => response.ok ? response.json() : Promise.reject())
    .then((data) => render(data.comments))
    .catch(() => { list.textContent = 'Comments are temporarily unavailable.' })

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    submit.disabled = true
    status.textContent = 'Sending your comment…'
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ post, name: form.elements.namedItem('name').value,
          body: form.elements.namedItem('body').value,
          website: form.elements.namedItem('website').value }),
      })
      if (!response.ok) throw new Error('Submission failed')
      form.reset()
      status.textContent = 'Thank you. Your comment is waiting for review.'
    } catch {
      status.textContent = 'Your comment could not be sent. Please try again later.'
    } finally {
      submit.disabled = false
    }
  })
})()
