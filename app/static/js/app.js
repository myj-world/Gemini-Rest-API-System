const form = document.getElementById('prompt-form');
const promptInput = document.getElementById('prompt');
const formatInput = document.getElementById('response-format');
const submitButton = document.getElementById('submit-button');
const buttonLabel = submitButton.querySelector('.button-label');
const spinner = submitButton.querySelector('.spinner');
const statusMessage = document.getElementById('status');
const resultSection = document.getElementById('result-section');
const resultElement = document.getElementById('result');
const copyButton = document.getElementById('copy-button');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const prompt = promptInput.value.trim();
  if (!prompt) {
    statusMessage.textContent = 'Enter a prompt to continue.';
    statusMessage.className = 'status error';
    promptInput.focus();
    return;
  }

  submitButton.disabled = true;
  buttonLabel.textContent = 'Generating…';
  spinner.classList.remove('hidden');
  statusMessage.textContent = '';
  statusMessage.className = 'status';
  resultSection.classList.add('hidden');

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        response_format: formatInput.value,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || 'The request could not be completed.');
    }

    resultElement.textContent = payload.response_format === 'json'
      ? JSON.stringify(payload.response, null, 2)
      : payload.response;
    resultSection.classList.remove('hidden');
  } catch (error) {
    statusMessage.textContent = error.message || 'Unable to reach the Gemini API.';
    statusMessage.className = 'status error';
  } finally {
    submitButton.disabled = false;
    buttonLabel.textContent = 'Generate response';
    spinner.classList.add('hidden');
  }
});

copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(resultElement.textContent);
    statusMessage.textContent = 'Response copied.';
    statusMessage.className = 'status success';
  } catch {
    statusMessage.textContent = 'Could not copy the response. Select and copy it instead.';
    statusMessage.className = 'status error';
  }
});
