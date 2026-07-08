const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("resumeFile");
const browseBtn = document.getElementById("browseBtn");
const fileName = document.getElementById("fileName");
const analyzeBtn = document.getElementById("analyzeBtn");
const matchJdBtn = document.getElementById("matchJdBtn");
const jdText = document.getElementById("jdText");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const downloadBtn = document.getElementById("downloadBtn");

let selectedFile = null;

browseBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) setFile(fileInput.files[0]);
});

["dragenter", "dragover"].forEach(evt => {
  dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach(evt => {
  dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
  });
});

dropZone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file && file.type === "application/pdf") setFile(file);
});

function setFile(file) {
  selectedFile = file;
  fileName.textContent = file.name;
  analyzeBtn.disabled = false;
  matchJdBtn.disabled = false;
}

function fillList(id, items, prefix = "") {
  const el = document.getElementById(id);
  el.innerHTML = "";
  (items || []).forEach(item => {
    const li = document.createElement("li");
    li.textContent = prefix ? `${prefix} ${item}` : item;
    el.appendChild(li);
  });
}

function fillTags(id, items) {
  const el = document.getElementById(id);
  el.innerHTML = "";
  (items || []).forEach(item => {
    const span = document.createElement("span");
    span.className = "tag";
    span.textContent = item;
    el.appendChild(span);
  });
}

function animateGauge(score) {
  const gauge = document.getElementById("gauge");
  const scoreText = document.getElementById("scoreText");
  let current = 0;
  const step = Math.max(1, Math.round(score / 40));

  const interval = setInterval(() => {
    current += step;
    if (current >= score) {
      current = score;
      clearInterval(interval);
    }
    scoreText.textContent = current;
    const degrees = (current / 100) * 360;
    const color = score >= 75 ? "#4ade80" : score >= 50 ? "#facc15" : "#f87171";
    gauge.style.background =
      `conic-gradient(${color} ${degrees}deg, #2a2d3a ${degrees}deg)`;
  }, 20);
}

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append("file", selectedFile);

  result.classList.add("hidden");
  loading.classList.remove("hidden");
  analyzeBtn.disabled = true;

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();

    animateGauge(data.ats_score);
    fillList("strengths", data.strengths, "✔");
    fillList("weaknesses", data.weaknesses, "•");
    fillTags("missingKeywords", data.missing_keywords);
    fillList("suggestions", data.suggestions);
    fillTags("suitableRoles", data.suitable_roles);
    document.getElementById("verdict").textContent = data.verdict;

    result.classList.remove("hidden");
  } catch (err) {
    alert("Something went wrong. Check the console.");
    console.error(err);
  } finally {
    loading.classList.add("hidden");
    analyzeBtn.disabled = false;
  }
});

matchJdBtn.addEventListener("click", async () => {
  if (!selectedFile) return;
  if (!jdText.value.trim()) {
    alert("Please paste a job description first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("job_description", jdText.value);

  result.classList.add("hidden");
  loading.classList.remove("hidden");
  matchJdBtn.disabled = true;

  try {
    const res = await fetch("/match-jd", { method: "POST", body: formData });
    const data = await res.json();

    animateGauge(data.ats_score);
    fillList("strengths", data.strengths, "✔");
    fillList("weaknesses", data.weaknesses, "•");
    fillTags("missingKeywords", data.missing_keywords);
    fillList("suggestions", data.suggestions);
    fillTags("suitableRoles", data.suitable_roles);
    document.getElementById("verdict").textContent =
      `${data.verdict} (JD Match: ${data.jd_match_percent}%)`;

    result.classList.remove("hidden");
  } catch (err) {
    alert("Something went wrong. Check the console.");
    console.error(err);
  } finally {
    loading.classList.add("hidden");
    matchJdBtn.disabled = false;
  }
});

downloadBtn.addEventListener("click", () => {
  window.print();
});