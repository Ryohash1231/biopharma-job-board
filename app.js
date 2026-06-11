async function init() {
  const response = await fetch('jobs.json');
  const data = await response.json();

  const lastUpdated = document.getElementById('last-updated');
  lastUpdated.textContent = `Last updated: ${new Date(data.scraped_at).toLocaleString()}`;

  const tbody = document.getElementById('jobs-body');
  const searchInput = document.getElementById('search');
  const recencySelect = document.getElementById('recency');

  const RECENCY_WINDOWS_MS = {
    '24h': 24 * 60 * 60 * 1000,
    '7d': 7 * 24 * 60 * 60 * 1000,
    '30d': 30 * 24 * 60 * 60 * 1000,
  };

  function withinRecency(job, bucket) {
    if (bucket === 'all') return true;
    if (!job.date_posted) return false;
    const postedTime = new Date(job.date_posted).getTime();
    return Date.now() - postedTime <= RECENCY_WINDOWS_MS[bucket];
  }

  function render(jobs) {
    tbody.innerHTML = '';
    for (const job of jobs) {
      const row = document.createElement('tr');

      const titleCell = document.createElement('td');
      const link = document.createElement('a');
      link.href = job.url;
      link.target = '_blank';
      link.rel = 'noopener';
      link.textContent = job.title;
      titleCell.appendChild(link);

      const companyCell = document.createElement('td');
      companyCell.textContent = job.company;

      const locationCell = document.createElement('td');
      locationCell.textContent = job.location;

      const postedCell = document.createElement('td');
      postedCell.textContent = job.date_posted
        ? new Date(job.date_posted).toLocaleDateString()
        : '—';

      row.append(titleCell, companyCell, locationCell, postedCell);
      tbody.appendChild(row);
    }
  }

  function applyFilter() {
    const query = searchInput.value.toLowerCase();
    const bucket = recencySelect.value;
    const filtered = data.jobs.filter(job =>
      (job.title.toLowerCase().includes(query) ||
      job.company.toLowerCase().includes(query) ||
      job.location.toLowerCase().includes(query)) &&
      withinRecency(job, bucket)
    );
    render(filtered);
  }

  searchInput.addEventListener('input', applyFilter);
  recencySelect.addEventListener('change', applyFilter);
  render(data.jobs);
}

init();
