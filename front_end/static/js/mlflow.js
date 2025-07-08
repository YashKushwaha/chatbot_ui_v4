// ====================== FETCH FUNCTIONS ======================

async function fetchExperiments() {
    const response = await fetch('/mlflow/list-experiments');
    if (!response.ok) throw new Error('Failed to fetch experiments');
    const data = await response.json();
    return data.experiments || [];
}

async function fetchTraces(experiment_id) {
    const response = await fetch(`/mlflow/list-traces?experiment_id=${encodeURIComponent(experiment_id)}`);
    if (!response.ok) throw new Error('Failed to fetch collections');
    const data = await response.json();
    return data.traces || [];
}

async function fetchTraceSummary(experiment_id, trace_id) {
    const response = await fetch(`/mlflow/list-trace-summary?experiment_id=${encodeURIComponent(experiment_id)}&trace_id=${encodeURIComponent(trace_id)}`);
    if (!response.ok) throw new Error('Failed to fetch trace summary');
    const data = await response.json();
    return data.span_summary || [];
}




// ====================== UI RENDER FUNCTIONS ======================

function createButton(label, cssClass, datasetProps = {}) {
    const btn = document.createElement('div');
    btn.textContent = label;
    btn.classList.add(cssClass);

    Object.entries(datasetProps).forEach(([key, value]) => {
        btn.dataset[key] = value;
    });

    return btn;
}

function showDBList(container, databases) {
    container.innerHTML = ""; // Clear existing list
    databases.forEach(dbName => {
        const dbButton = createButton(dbName.name, 'list-item', { ...dbName });
        container.appendChild(dbButton);
    });
}

function showCollections(container, dbName, collections) {
    container.innerHTML = "";
    
    collections.forEach(colName => {
         const colButton = createButton(colName.start_time_str, 'list-item', { ...colName });
        container.appendChild(colButton);
    });
}

function showSpanSummary(container, experiment_id, trace_id, summary_list) {
    container.innerHTML = "";
    
    summary_list.forEach(colName => {
        div = document.createElement('div');
        console.log('ColNam => ', colName);
        const htmlContent = marked.parse(colName);
        div.innerHTML = htmlContent;
        container.appendChild(div);

    });
}

// ====================== EVENT HANDLERS ======================

function handleDBClick(e) {
    if (!e.target.classList.contains('list-item')) return;

    const dbName = e.target.dataset.experiment_id;
    const collectionContainer = document.getElementById('collections-list');

    window.selectionState.dbName = dbName

    fetchTraces(dbName)
        .then(traces => {
                showCollections(collectionContainer, dbName, traces);
            })
        .catch(err => console.error(err));

    toggleActiveState(e.target, '.list-item');
}

function handleCollectionClick(e) {
    if (!e.target.classList.contains('list-item')) return;

    toggleActiveState(e.target, '.list-item');

    const experiment_id = e.target.dataset.experiment_id;
    const trace_id = e.target.dataset.trace_id;
    const container = document.getElementById('record-value-counts')
    fetchTraceSummary(experiment_id, trace_id)
    .then(span_summary => {
            showSpanSummary(container, experiment_id,trace_id, span_summary)
        }
    )


 }

function toggleActiveState(target, selector) {
    const allButtons = document.querySelectorAll(selector);
    allButtons.forEach(btn => btn.classList.remove('active'));
    target.classList.add('active');
}


// ====================== INITIALIZATION ======================

window.selectionState = {
    dbName: null,
    colName: null,
    field: null,
    value: null
};

document.addEventListener('DOMContentLoaded', () => {
    const dbListContainer = document.getElementById('experiment-list');
    const collectionListContainer = document.getElementById('collections-list');
    const recordValueCountsDiv = document.getElementById('record-value-counts');
    // Fetch and show databases
    fetchExperiments()
        .then(experiments => showDBList(dbListContainer, experiments))
        .catch(err => console.error(err));

    // Attach event listeners
    dbListContainer.addEventListener('click', handleDBClick);
    collectionListContainer.addEventListener('click', handleCollectionClick);

});
