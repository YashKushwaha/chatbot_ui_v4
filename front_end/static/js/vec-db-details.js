async function fetchCollections() {
    const response = await fetch(`/vecdb/list-collections`);
    if (!response.ok) throw new Error('Failed to fetch collections');
    const data = await response.json();
    return data.collections || [];
}

async function fetchNumRecords(collection) {
    const response = await fetch(`/vecdb/num-records-in-collection?collection=${encodeURIComponent(collection)}`);
    if (!response.ok) throw new Error('Failed to fetch number of records');
    const data = await response.json();
    return data.num_records || 0;
}

async function fetchFirstNRecords(collection) {
    const response = await fetch(`/vecdb/first-n-records-in-collection?collection=${encodeURIComponent(collection)}`);
    if (!response.ok) throw new Error('Failed to fetch number of records');
    const data = await response.json();
    return data.records || [];
}

function showCollections(container, collections) {
    container.innerHTML = "default_database";
    const dbName = ""
    collections.forEach(colName => {
        const colButton = createButton(colName, 'collection-button', { dbName, colName });
        container.appendChild(colButton);
    });
}

function createButton(label, cssClass, datasetProps = {}) {
    const btn = document.createElement('div');
    btn.textContent = label;
    btn.classList.add(cssClass);

    Object.entries(datasetProps).forEach(([key, value]) => {
        btn.dataset[key] = value;
    });

    return btn;
}

function toggleActiveState(target, selector) {
    const allButtons = document.querySelectorAll(selector);
    allButtons.forEach(btn => btn.classList.remove('active'));
    target.classList.add('active');
}

function handleCollectionClick(e) {
    if (!e.target.classList.contains('collection-button')) return;

    const colName = e.target.dataset.colName;

    const recordCountDiv = document.getElementById('record-count');
    const recordContentDiv = document.getElementById('record-content');

    // Optional: Indicate loading state
    recordCountDiv.innerHTML = `<p>Loading count...</p>`;
    recordContentDiv.innerHTML = `<p>Loading records...</p>`;

    fetchNumRecords(colName)
        .then(count => {
            recordCountDiv.innerHTML = `<p>Total Records: ${count}</p>`;
        })
        .catch(err => {
            console.error(err);
            recordCountDiv.innerHTML = `<p style="color:red;">Failed to fetch record count</p>`;
        });

    fetchFirstNRecords(colName)
        .then(records => {
        recordContentDiv.innerHTML = '';
        records.forEach(record => {
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            code.classList.add('json');  // Apply JSON highlighting
            // Generate pretty JSON without extra escaping for quotes
            const formattedJson = JSON.stringify(record, null, 2);

            // Set as textContent (so it won't double-escape) and rely on highlight.js
            code.textContent = formattedJson;
            pre.appendChild(code);
            recordContentDiv.appendChild(pre);
            hljs.highlightElement(code);  // Apply highlighting
        });
    
    });

    toggleActiveState(e.target, '.collection-button');
}

document.addEventListener('DOMContentLoaded', () => {
    const collectionListContainer = document.getElementById('collections-list');

    // Fetch and show databases
    fetchCollections()
        .then(collections => showCollections(collectionListContainer, collections))
        .catch(err => console.error(err));

    // Attach event listeners
    collectionListContainer.addEventListener('click', handleCollectionClick);
});