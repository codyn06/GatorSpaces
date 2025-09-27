(function(){})();
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const URL = 'https://www.uflib.ufl.edu/status/';

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(URL, { waitUntil: 'networkidle' }); // wait for JS to load
  await page.waitForTimeout(5000); // extra wait for dynamic content

  // Get all visible text on the page
  const renderedText = await page.innerText('body');

  await browser.close();

  function safeSlice(text, startStr, endStr) {
    const start = text.indexOf(startStr);
    if (start === -1) return null;
    if (!endStr) return text.slice(start);
    const end = text.indexOf(endStr, start + startStr.length);
    if (end === -1) return text.slice(start);
    return text.slice(start, end);
  }

  function parseCounts(block) {
    if (!block) return { occupancy: null, capacity: null };
    const occMatch = block.match(/Occupancy\s*[:\n]*\s*(\d+)/i);
    const capMatch = block.match(/Capacity\s*[:\s]*?(\d+)/i);
    const occupancy = occMatch ? parseInt(occMatch[1], 10) : null;
    const capacity = capMatch ? parseInt(capMatch[1], 10) : null;
    return { occupancy, capacity };
  }

  const LibraryWestBlock = safeSlice(renderedText, 'Library West', 'Marston');
  const MarstonBlock = safeSlice(renderedText, 'Marston', 'Health');
  const HealthBlock = safeSlice(renderedText, 'Health', 'Architecture');
  const ArchitectureBlock = safeSlice(renderedText, 'Architecture', 'Education');
  const EducationBlock = safeSlice(renderedText, 'Education', 'Smathers');
  const SmathersBlock = safeSlice(renderedText, 'Smathers Library');

  const data = {
    timestamp: new Date().toISOString(),
    libraries: {
      libwest: parseCounts(LibraryWestBlock),
      marston: parseCounts(MarstonBlock),
      health: parseCounts(HealthBlock),
      afa: parseCounts(ArchitectureBlock),
      education: parseCounts(EducationBlock),
      smathers: parseCounts(SmathersBlock),
    },
  };

  function statusFromCounts({ occupancy, capacity }) {
    if (occupancy == null || capacity == null || capacity === 0) return 'Unknown';
    const ratio = occupancy / capacity;
    if (ratio >= 0.7) return 'High';
    if (ratio >= 0.3) return 'Medium';
    return 'Low';
  }

  const output = { timestamp: data.timestamp, results: {} };
  for (const [id, counts] of Object.entries(data.libraries)) {
    output.results[id] = {
      occupancy: counts.occupancy,
      capacity: counts.capacity,
      status: statusFromCounts(counts),
    };
  }

  // Write library_status.json (used by the frontend)
  const statusPath = path.join(__dirname, 'library_status.json');
  fs.writeFileSync(statusPath, JSON.stringify(output, null, 2), 'utf8');
  console.log('Wrote', statusPath);

  // Also write a live data file merging IDs with live fields
  const live = { timestamp: data.timestamp, libraries: {} };
  for (const [id, info] of Object.entries(output.results)) {
    live.libraries[id] = {
      occupancy: info.occupancy,
      capacity: info.capacity,
      baseStatus: info.status,
    };
  }
  const livePath = path.join(__dirname, 'library_data_live.json');
  fs.writeFileSync(livePath, JSON.stringify(live, null, 2), 'utf8');
  console.log('Wrote', livePath);

  console.log(JSON.stringify(output, null, 2));
})();
(async () => {
  const URL = 'https://www.uflib.ufl.edu/status/';

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(URL, { waitUntil: 'networkidle' }); // wait for JS to load
  await page.waitForTimeout(5000); // extra wait for dynamic content

  // Get all visible text on the page
  const renderedText = await page.innerText('body');

  await browser.close();

  // Helper to mimic Python slicing by index
  function safeSlice(text, startStr, endStr) {
    const start = text.indexOf(startStr);
    if (start === -1) return null;
    if (!endStr) return text.slice(start);
    const end = text.indexOf(endStr, start + startStr.length);
    if (end === -1) return text.slice(start);
    return text.slice(start, end);
  }

  const LibraryWest = safeSlice(renderedText, 'Library West', 'Marston');
  const Marston = safeSlice(renderedText, 'Marston', 'Health');
  const HealthScience = safeSlice(renderedText, 'Health', 'Architecture');
  const Architecture = safeSlice(renderedText, 'Architecture', 'Education');
  const Education = safeSlice(renderedText, 'Education', 'Smathers');

  let Smathers = null;
  const smIndex = renderedText.indexOf('Smathers Library');
  if (smIndex !== -1) {
    const idx231 = renderedText.indexOf('231', smIndex);
    if (idx231 !== -1) {
      Smathers = renderedText.slice(smIndex, idx231 + 4);
    } else {
      Smathers = renderedText.slice(smIndex);
    }
  }

  // Print in same order as Python script
  console.log(Smathers, Education, LibraryWest, Marston, HealthScience, Architecture);
})();
