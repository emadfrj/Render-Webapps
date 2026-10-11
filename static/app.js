const list = document.querySelector('#task-list');
const form = document.querySelector('#task-form');
const input = document.querySelector('#task-input');
const error = document.querySelector('#form-error');
const count = document.querySelector('#task-count');
const emptyState = document.querySelector('#empty-state');

document.querySelector('#today').textContent = new Intl.DateTimeFormat(undefined, {
  weekday: 'short', month: 'short', day: 'numeric'
}).format(new Date());

async function request(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Something went wrong.');
  return data;
}

function render(tasks) {
  list.replaceChildren();
  const remaining = tasks.filter(task => !task.done).length;
  count.textContent = remaining === 0 ? 'All done' : `${remaining} left`;
  emptyState.hidden = tasks.length > 0;
  for (const task of tasks) {
    const item = document.createElement('li');
    item.className = `task-item${task.done ? ' is-done' : ''}`;
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'check-button';
    toggle.setAttribute('aria-label', `${task.done ? 'Mark' : 'Complete'} ${task.title}`);
    toggle.setAttribute('aria-pressed', String(task.done));
    toggle.textContent = task.done ? '✓' : '';
    toggle.addEventListener('click', async () => {
      try { render(await request(`/api/tasks/${task.id}`, { method: 'PATCH' }).then(() => request('/api/tasks'))); }
      catch (err) { error.textContent = err.message; }
    });
    const title = document.createElement('span');
    title.className = 'task-title';
    title.textContent = task.title;
    item.append(toggle, title);
    list.append(item);
  }
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  error.textContent = '';
  try {
    await request('/api/tasks', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: input.value })
    });
    input.value = '';
    render(await request('/api/tasks'));
    input.focus();
  } catch (err) { error.textContent = err.message; }
});

request('/api/tasks').then(render).catch(err => { error.textContent = err.message; });
