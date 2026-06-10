async function init() {
  const response = await fetch('jobs.json');
  const data = await response.json();

  const lastUpdated = document.getElementById('last-updated');
  lastUpdated.textContent = `Last updated: ${new Date(data.scraped_at).toLocaleString()}`;

  const tbody = document.getElementById('jobs-body');
  const searchInput = document.getElementById('search');

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

      row.append(titleCell, companyCell, locationCell);
      tbody.appendChild(row);
    }
  }

  function applyFilter() {
    const query = searchInput.value.toLowerCase();
    const filtered = data.jobs.filter(job =>
      job.title.toLowerCase().includes(query) ||
      job.company.toLowerCase().includes(query) ||
      job.location.toLowerCase().includes(query)
    );
    render(filtered);
  }

  searchInput.addEventListener('input', applyFilter);
  render(data.jobs);
}

init();
