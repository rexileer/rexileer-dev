document.querySelector('[data-copy-credit]')?.addEventListener('click', async () => {
  const field = document.getElementById('credit-copy');
  const status = document.getElementById('copy-status');
  try {
    await navigator.clipboard.writeText(field.value);
    status.textContent = 'Текст скопирован';
  } catch {
    field.focus();
    field.select();
    status.textContent = 'Текст выделен — скопируйте вручную';
  }
});
