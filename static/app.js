const inputText =
  document.getElementById("inputText");

const markdownOutput =
  document.getElementById("markdownOutput");

const previewOutput =
  document.getElementById("previewOutput");

const instructionInput =
  document.getElementById("instructionInput");

const fileNameInput =
  document.getElementById("fileNameInput");

const modeSelect =
  document.getElementById("modeSelect");

const languageSelect =
  document.getElementById("languageSelect");

const detailSelect =
  document.getElementById("detailSelect");

const organizeButton =
  document.getElementById("organizeButton");

const cancelButton =
  document.getElementById("cancelButton");

const clearButton =
  document.getElementById("clearButton");

const copyButton =
  document.getElementById("copyButton");

const downloadButton =
  document.getElementById("downloadButton");

const markdownTab =
  document.getElementById("markdownTab");

const previewTab =
  document.getElementById("previewTab");

const statusPill =
  document.getElementById("statusPill");

const inputCharacters =
  document.getElementById("inputCharacters");

const inputWords =
  document.getElementById("inputWords");

const outputCharacters =
  document.getElementById("outputCharacters");

const processingTime =
  document.getElementById("processingTime");

const liveTimer =
  document.getElementById("liveTimer");

const progressBar =
  document.getElementById("progressBar");

const progressPercent =
  document.getElementById("progressPercent");

const validationBox =
  document.getElementById("validationBox");

const githubStarCount =
  document.getElementById("githubStarCount");

const githubStarLink =
  document.getElementById("githubStarLink");


const GITHUB_REPO =
  "Al-Jid/ReMindly-Agent";

const GITHUB_REPO_URL =
  `https://github.com/${GITHUB_REPO}`;

const GITHUB_API_URL =
  `https://api.github.com/repos/${GITHUB_REPO}`;


let abortController = null;

let timerInterval = null;

let timerStartedAt = null;

let currentMarkdown = "";

let currentStage = null;


const STORAGE_KEY =
  "md-notes-agent-draft-v2";


const stageOrder = [
  "input_received",
  "preparing",
  "generating",
  "validating",
  "reviewing",
  "finalizing",
];


function setStatus(
  text,
  type = "",
) {
  statusPill.textContent = text;

  statusPill.className =
    `status-pill ${type}`.trim();
}


function updateProgress(
  value,
) {
  const safeValue =
    Math.max(
      0,
      Math.min(100, value),
    );

  progressBar.style.width =
    `${safeValue}%`;

  progressPercent.textContent =
    `${safeValue}%`;
}


function getProcessElement(
  stage,
) {
  return document.querySelector(
    `[data-stage="${stage}"]`
  );
}


function setProcessStage(
  stage,
) {
  currentStage = stage;

  const currentIndex =
    stageOrder.indexOf(stage);

  stageOrder.forEach(
    (stageName, index) => {
      const element =
        getProcessElement(stageName);

      if (!element) {
        return;
      }

      const icon =
        element.querySelector(
          ".process-icon"
        );

      element.classList.remove(
        "active",
        "done",
        "skipped",
        "error",
      );

      if (index < currentIndex) {
        element.classList.add(
          "done"
        );

        icon.textContent = "✓";
      }

      else if (
        index === currentIndex
      ) {
        element.classList.add(
          "active"
        );

        icon.textContent = "●";
      }

      else {
        icon.textContent = "○";
      }
    }
  );
}


function markProcessCompleted(
  reviewed = false
) {
  stageOrder.forEach(
    (stageName) => {
      const element =
        getProcessElement(
          stageName
        );

      if (!element) {
        return;
      }

      element.classList.remove(
        "active"
      );

      const icon =
        element.querySelector(
          ".process-icon"
        );

      if (
        stageName === "reviewing"
        &&
        !reviewed
      ) {
        element.classList.remove(
          "done"
        );

        element.classList.add(
          "skipped"
        );

        icon.textContent = "–";
      }

      else {
        element.classList.add(
          "done"
        );

        icon.textContent = "✓";
      }
    }
  );
}


function markProcessError() {
  if (!currentStage) {
    return;
  }

  const element =
    getProcessElement(
      currentStage
    );

  if (!element) {
    return;
  }

  element.classList.remove(
    "active"
  );

  element.classList.add(
    "error"
  );

  const icon =
    element.querySelector(
      ".process-icon"
    );

  icon.textContent = "!";
}


function resetProcess() {
  currentStage = null;

  updateProgress(0);

  stageOrder.forEach(
    (stageName) => {
      const element =
        getProcessElement(
          stageName
        );

      if (!element) {
        return;
      }

      element.classList.remove(
        "active",
        "done",
        "skipped",
        "error",
      );

      element.querySelector(
        ".process-icon"
      ).textContent = "○";
    }
  );

  validationBox.className =
    "validation-box hidden";

  validationBox.innerHTML = "";
}


function startTimer() {
  stopTimer();

  timerStartedAt =
    performance.now();

  liveTimer.textContent =
    "0.0s";

  timerInterval =
    setInterval(
      () => {
        const elapsed =
          (
            performance.now()
            -
            timerStartedAt
          )
          /
          1000;

        liveTimer.textContent =
          `${elapsed.toFixed(1)}s`;
      },
      100,
    );
}


function stopTimer() {
  if (timerInterval) {
    clearInterval(
      timerInterval
    );

    timerInterval = null;
  }
}


function updateInputStats() {
  const text =
    inputText.value;

  inputCharacters.textContent =
    text.length;

  const words =
    text.trim()
      ? text
        .trim()
        .split(/\s+/)
        .length
      : 0;

  inputWords.textContent =
    words;
}


function updateOutputStats() {
  outputCharacters.textContent =
    markdownOutput.value.length;
}


function sanitizeFileName(
  name,
) {
  const cleaned =
    name
      .trim()
      .replace(
        /[<>:"/\\|?*\u0000-\u001F]/g,
        "-"
      )
      .replace(
        /\s+/g,
        "-"
      )
      .replace(
        /-+/g,
        "-"
      )
      .replace(
        /^-|-$/g,
        ""
      );

  return (
    cleaned
    || "organized-notes"
  );
}


function saveDraft() {
  const state = {
    inputText:
      inputText.value,

    markdown:
      markdownOutput.value,

    instruction:
      instructionInput.value,

    fileName:
      fileNameInput.value,

    mode:
      modeSelect.value,

    language:
      languageSelect.value,

    detail:
      detailSelect.value,
  };

  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(state),
  );
}


function restoreDraft() {
  const saved =
    localStorage.getItem(
      STORAGE_KEY
    );

  if (!saved) {
    return;
  }

  try {
    const state =
      JSON.parse(saved);

    inputText.value =
      state.inputText || "";

    markdownOutput.value =
      state.markdown || "";

    currentMarkdown =
      markdownOutput.value;

    instructionInput.value =
      state.instruction || "";

    fileNameInput.value =
      state.fileName || "";

    if (state.mode) {
      modeSelect.value =
        state.mode;
    }

    if (state.language) {
      languageSelect.value =
        state.language;
    }

    if (state.detail) {
      detailSelect.value =
        state.detail;
    }

    updateInputStats();

    updateOutputStats();

    const hasOutput =
      Boolean(
        markdownOutput.value
          .trim()
      );

    copyButton.disabled =
      !hasOutput;

    downloadButton.disabled =
      !hasOutput;
  }

  catch (error) {
    console.warn(
      "Could not restore draft:",
      error,
    );
  }
}


function setRunningState(
  running,
) {
  organizeButton.disabled =
    running;

  cancelButton.classList.toggle(
    "hidden",
    !running,
  );

  if (running) {
    organizeButton.textContent =
      "Processing...";
  }

  else {
    organizeButton.textContent =
      "Organize Notes";
  }
}


function showValidation(
  validation,
  reviewed,
) {
  validationBox.className =
    "validation-box";

  const issues =
    validation?.issues || [];

  if (
    validation?.valid
    &&
    issues.length === 0
  ) {
    validationBox.classList.add(
      "success"
    );

    validationBox.innerHTML =
      reviewed
        ? "✓ Quality review completed. Markdown passed validation."
        : "✓ Markdown passed local validation.";

    return;
  }

  const hasError =
    issues.some(
      issue =>
        issue.severity
        === "error"
    );

  validationBox.classList.add(
    hasError
      ? "error"
      : "warning"
  );

  const list =
    issues
      .map(
        issue =>
          `<li><strong>${escapeHtml(
            issue.code
          )}</strong>: ${escapeHtml(
            issue.message
          )}</li>`
      )
      .join("");

  validationBox.innerHTML =
    `
      <strong>
        ${hasError
      ? "Validation problems detected:"
      : "Validation warnings:"
    }
      </strong>

      <ul>
        ${list}
      </ul>
    `;
}


function escapeHtml(
  value,
) {
  return String(value)
    .replace(
      /&/g,
      "&amp;"
    )
    .replace(
      /</g,
      "&lt;"
    )
    .replace(
      />/g,
      "&gt;"
    )
    .replace(
      /"/g,
      "&quot;"
    )
    .replace(
      /'/g,
      "&#039;"
    );
}


function updatePreview() {
  const markdown =
    markdownOutput.value;

  if (
    typeof marked
    === "undefined"
  ) {
    previewOutput.textContent =
      markdown;

    return;
  }

  const rendered =
    marked.parse(
      markdown
    );

  if (
    typeof DOMPurify
    !== "undefined"
  ) {
    previewOutput.innerHTML =
      DOMPurify.sanitize(
        rendered
      );

    return;
  }

  /*
   * Fail safely.
   *
   * If DOMPurify failed to load,
   * do not inject generated HTML.
   */
  previewOutput.textContent =
    markdown;
}


function handleProgressEvent(
  data,
) {
  if (data.stage) {
    setProcessStage(
      data.stage
    );
  }

  if (
    typeof data.progress
    === "number"
  ) {
    updateProgress(
      data.progress
    );
  }

  if (data.label) {
    setStatus(
      data.label,
      "working",
    );
  }
}


function handleTokenEvent(
  data,
) {
  const chunk =
    data.text || "";

  currentMarkdown += chunk;

  markdownOutput.value =
    currentMarkdown;

  updateOutputStats();

  markdownOutput.scrollTop =
    markdownOutput.scrollHeight;

  if (
    typeof data.output_characters
    === "number"
  ) {
    outputCharacters.textContent =
      data.output_characters;
  }
}


function handleReplaceEvent(
  data,
) {
  if (
    typeof data.markdown
    !== "string"
  ) {
    return;
  }

  currentMarkdown =
    data.markdown;

  markdownOutput.value =
    currentMarkdown;

  updateOutputStats();

  markdownOutput.scrollTop =
    markdownOutput.scrollHeight;
}


function handleCompletedEvent(
  data,
) {
  if (
    typeof data.markdown
    === "string"
  ) {
    currentMarkdown =
      data.markdown;

    markdownOutput.value =
      currentMarkdown;

    updateOutputStats();
  }

  processingTime.textContent =
    `${Number(
      data.processing_time || 0
    ).toFixed(1)}s`;

  liveTimer.textContent =
    `${Number(
      data.processing_time || 0
    ).toFixed(1)}s`;

  updateProgress(100);

  markProcessCompleted(
    Boolean(data.reviewed)
  );

  setStatus(
    "Completed",
    "success",
  );

  showValidation(
    data.validation,
    data.reviewed,
  );

  copyButton.disabled =
    !currentMarkdown.trim();

  downloadButton.disabled =
    !currentMarkdown.trim();

  saveDraft();

  updatePreview();
}


function parseSSEBlock(
  block,
) {
  const lines =
    block.split("\n");

  let eventName =
    "message";

  const dataLines = [];

  for (
    const line of lines
  ) {
    if (
      line.startsWith(
        "event:"
      )
    ) {
      eventName =
        line
          .slice(6)
          .trim();
    }

    else if (
      line.startsWith(
        "data:"
      )
    ) {
      dataLines.push(
        line
          .slice(5)
          .trimStart()
      );
    }
  }

  if (
    dataLines.length === 0
  ) {
    return null;
  }

  const rawData =
    dataLines.join("\n");

  let data;

  try {
    data =
      JSON.parse(rawData);
  }

  catch {
    data = {
      text: rawData,
    };
  }

  return {
    event:
      eventName,

    data,
  };
}


function processParsedSSEEvent(
  parsedEvent,
) {
  const {
    event: eventName,
    data,
  } = parsedEvent;

  if (
    eventName
    === "progress"
  ) {
    handleProgressEvent(
      data
    );

    return false;
  }

  if (
    eventName
    === "token"
  ) {
    handleTokenEvent(
      data
    );

    return false;
  }

  if (
    eventName
    === "replace"
  ) {
    handleReplaceEvent(
      data
    );

    return false;
  }

  if (
    eventName
    === "completed"
  ) {
    handleCompletedEvent(
      data
    );

    return true;
  }

  if (
    eventName
    === "error"
  ) {
    throw new Error(
      data.message
      || "Unknown processing error."
    );
  }

  return false;
}


async function processSSEStream(
  response,
) {
  if (!response.body) {
    throw new Error(
      "Streaming response is unavailable."
    );
  }

  const reader =
    response.body.getReader();

  const decoder =
    new TextDecoder(
      "utf-8"
    );

  let buffer = "";

  let completed = false;

  while (true) {
    const {
      value,
      done,
    } =
      await reader.read();

    if (done) {
      /*
       * Flush any remaining bytes
       * held by TextDecoder.
       */
      buffer +=
        decoder.decode();

      break;
    }

    buffer +=
      decoder.decode(
        value,
        {
          stream: true,
        }
      );

    buffer =
      buffer.replace(
        /\r\n/g,
        "\n"
      );

    let boundaryIndex;

    while (
      (
        boundaryIndex =
        buffer.indexOf(
          "\n\n"
        )
      )
      !== -1
    ) {
      const block =
        buffer
          .slice(
            0,
            boundaryIndex
          )
          .trim();

      buffer =
        buffer.slice(
          boundaryIndex + 2
        );

      if (!block) {
        continue;
      }

      const parsedEvent =
        parseSSEBlock(
          block
        );

      if (!parsedEvent) {
        continue;
      }

      const eventCompleted =
        processParsedSSEEvent(
          parsedEvent
        );

      if (eventCompleted) {
        completed = true;
      }
    }
  }

  /*
   * Handle a final SSE event
   * even if the connection ended
   * without a trailing blank line.
   */
  const remainingBlock =
    buffer.trim();

  if (remainingBlock) {
    const parsedEvent =
      parseSSEBlock(
        remainingBlock
      );

    if (parsedEvent) {
      const eventCompleted =
        processParsedSSEEvent(
          parsedEvent
        );

      if (eventCompleted) {
        completed = true;
      }
    }
  }

  if (!completed) {
    throw new Error(
      "The connection ended before processing completed."
    );
  }
}


async function organizeNotes() {
  const text =
    inputText.value.trim();

  if (!text) {
    setStatus(
      "Paste some text first",
      "error",
    );

    inputText.focus();

    return;
  }

  abortController =
    new AbortController();

  currentMarkdown = "";

  markdownOutput.value = "";

  previewOutput.textContent = "";

  updateOutputStats();

  processingTime.textContent =
    "0.0s";

  resetProcess();

  setRunningState(true);

  setStatus(
    "Starting...",
    "working",
  );

  copyButton.disabled = true;

  downloadButton.disabled = true;

  startTimer();

  const body = {
    text,

    instruction:
      instructionInput
        .value
        .trim()
      || null,

    mode:
      modeSelect.value,

    language:
      languageSelect.value,

    detail_level:
      detailSelect.value,
  };

  try {
    const response =
      await fetch(
        "/api/organize/stream",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body:
            JSON.stringify(
              body
            ),

          signal:
            abortController.signal,
        }
      );

    if (!response.ok) {
      let message =
        `HTTP ${response.status}`;

      try {
        const data =
          await response.json();

        if (
          typeof data.detail
          === "string"
        ) {
          message = data.detail;
        }

        else if (
          data.detail?.message
        ) {
          message =
            data.detail.message;
        }

        else if (data.error) {
          message =
            data.error;
        }
      }

      catch {
        // Ignore JSON parsing failure.
      }

      throw new Error(
        message
      );
    }

    await processSSEStream(
      response
    );
  }

  catch (error) {
    if (
      error.name
      === "AbortError"
    ) {
      setStatus(
        "Cancelled",
        "error",
      );

      validationBox.className =
        "validation-box warning";

      validationBox.textContent =
        "Generation was cancelled by the user.";
    }

    else {
      console.error(
        error
      );

      markProcessError();

      setStatus(
        "Error",
        "error",
      );

      validationBox.className =
        "validation-box error";

      validationBox.textContent =
        error.message
        || "Unknown error.";
    }
  }

  finally {
    stopTimer();

    setRunningState(
      false
    );

    abortController = null;

    saveDraft();
  }
}


organizeButton.addEventListener(
  "click",
  organizeNotes,
);


cancelButton.addEventListener(
  "click",
  () => {
    if (abortController) {
      abortController.abort();
    }
  },
);


clearButton.addEventListener(
  "click",
  () => {
    if (abortController) {
      abortController.abort();
    }

    inputText.value = "";

    markdownOutput.value = "";

    previewOutput.textContent = "";

    instructionInput.value = "";

    fileNameInput.value = "";

    currentMarkdown = "";

    updateInputStats();

    updateOutputStats();

    processingTime.textContent =
      "0.0s";

    liveTimer.textContent =
      "0.0s";

    resetProcess();

    setStatus(
      "Ready"
    );

    copyButton.disabled =
      true;

    downloadButton.disabled =
      true;

    localStorage.removeItem(
      STORAGE_KEY
    );

    inputText.focus();
  },
);


copyButton.addEventListener(
  "click",
  async () => {
    const text =
      markdownOutput.value;

    if (!text.trim()) {
      return;
    }

    try {
      await navigator
        .clipboard
        .writeText(
          text
        );

      setStatus(
        "Copied",
        "success",
      );
    }

    catch {
      setStatus(
        "Copy failed",
        "error",
      );
    }
  },
);


downloadButton.addEventListener(
  "click",
  () => {
    const markdown =
      markdownOutput.value;

    if (!markdown.trim()) {
      return;
    }

    const blob =
      new Blob(
        [markdown],
        {
          type:
            "text/markdown;charset=utf-8",
        }
      );

    const url =
      URL.createObjectURL(
        blob
      );

    const anchor =
      document.createElement(
        "a"
      );

    anchor.href = url;

    anchor.download =
      `${sanitizeFileName(
        fileNameInput.value
      )}.md`;

    document.body.appendChild(
      anchor
    );

    anchor.click();

    anchor.remove();

    URL.revokeObjectURL(
      url
    );

    setStatus(
      "Downloaded",
      "success",
    );
  },
);


markdownTab.addEventListener(
  "click",
  () => {
    markdownTab.classList.add(
      "active"
    );

    previewTab.classList.remove(
      "active"
    );

    markdownOutput.classList.remove(
      "hidden"
    );

    previewOutput.classList.add(
      "hidden"
    );
  },
);


previewTab.addEventListener(
  "click",
  () => {
    updatePreview();

    previewTab.classList.add(
      "active"
    );

    markdownTab.classList.remove(
      "active"
    );

    previewOutput.classList.remove(
      "hidden"
    );

    markdownOutput.classList.add(
      "hidden"
    );
  },
);


inputText.addEventListener(
  "input",
  () => {
    updateInputStats();

    saveDraft();
  },
);


markdownOutput.addEventListener(
  "input",
  () => {
    currentMarkdown =
      markdownOutput.value;

    updateOutputStats();

    saveDraft();

    if (
      !previewOutput
        .classList
        .contains(
          "hidden"
        )
    ) {
      updatePreview();
    }
  },
);


instructionInput.addEventListener(
  "input",
  saveDraft,
);


fileNameInput.addEventListener(
  "input",
  saveDraft,
);


modeSelect.addEventListener(
  "change",
  saveDraft,
);


languageSelect.addEventListener(
  "change",
  saveDraft,
);


detailSelect.addEventListener(
  "change",
  saveDraft,
);


/*
 * GitHub Star Counter
 *
 * Gets the current number of stars
 * directly from GitHub's public API.
 */
async function loadGitHubStars() {
  if (!githubStarCount) {
    return;
  }

  if (githubStarLink) {
    githubStarLink.href =
      GITHUB_REPO_URL;
  }

  const controller =
    new AbortController();

  const timeoutId =
    setTimeout(
      () => {
        controller.abort();
      },
      5000,
    );

  try {
    const response =
      await fetch(
        GITHUB_API_URL,
        {
          headers: {
            Accept:
              "application/vnd.github+json",
          },

          signal:
            controller.signal,
        },
      );

    if (!response.ok) {
      throw new Error(
        `GitHub API HTTP ${response.status}`
      );
    }

    const data =
      await response.json();

    const stars =
      Number(
        data.stargazers_count
      );

    if (!Number.isFinite(stars)) {
      throw new Error(
        "Invalid GitHub star count."
      );
    }

    githubStarCount.textContent =
      new Intl.NumberFormat()
        .format(stars);

    githubStarCount.title =
      `${stars} GitHub stars`;
  }

  catch (error) {
    githubStarCount.textContent =
      "";

    console.warn(
      "Could not load GitHub stars:",
      error,
    );
  }

  finally {
    clearTimeout(timeoutId);
  }
}


restoreDraft();

loadGitHubStars();

updateInputStats();

updateOutputStats();

setStatus(
  "Ready"
);

inputText.focus();
