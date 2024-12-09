const canvasContainer = document.getElementById("canvas-div");
const canvas = document.getElementById("canvas");

const makeArc = (ctx, x, y, left, up, r) => {
    if (left && up) {
        ctx.moveTo(x, y + r);
        ctx.arc(x, y, r, Math.PI / 2, Math.PI);
    }
    if (!left && up) {
        ctx.moveTo(x + r, y);
        ctx.arc(x, y, r, 0, Math.PI / 2);
    }
    if (left && !up) {
        ctx.moveTo(x - r, y)
        ctx.arc(x, y, r, Math.PI, 3 * Math.PI / 2);
    }
    if (!left && !up) {
        ctx.moveTo(x, y - r);
        ctx.arc(x, y, r, 3 * Math.PI / 2, 2 * Math.PI);
    }
}

let divs = [];
let oldConnections = [];

const createDiv = (x, y, r, idx) => {
    const div = document.createElement("div");
    div.style.left = x - r + "px";
    div.style.top = y - r + "px";
    div.style.width = r * 2 + "px";
    div.style.height = r * 2 + "px";
    div.classList.add("circle-button");
    divs.push(div);
    div.addEventListener("click", () => {
        if (connections[idx] === undefined || connections[idx][2] === undefined) {
            return;
        }
        connections[idx][2] = 1 - connections[idx][2];
    });
    canvasContainer.appendChild(div);
}
const renderConnections = () => {

    const newConnections = [];

    connections.forEach((connection, idx) => {

        const a = connection[0];
        const b = connection[1];
        const type = connection[2];
        const aRect = a.getBoundingClientRect();
        const bRect = b.getBoundingClientRect();
        const cRect = canvas.getBoundingClientRect();
        const aX = aRect.left + aRect.width / 2 - cRect.left;
        const aY = aRect.top + aRect.height / 2 - cRect.top;
        const bX = bRect.left + bRect.width / 2 - cRect.left;
        const bY = bRect.top + bRect.height / 2 - cRect.top;
        newConnections.push(...[aX, aY, bX, bY, type, idx]);
    });

    if (JSON.stringify(oldConnections) === JSON.stringify(newConnections)) {
        return;
    }
    const ctx = canvas.getContext("2d");

    divs.forEach((div) => {
        div.remove();
    });
    divs = [];
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    oldConnections = newConnections;
    connections.forEach((connection, idx) => {

        const a = connection[0];
        const b = connection[1];
        const type = connection[2];
        const aRect = a.getBoundingClientRect();
        const bRect = b.getBoundingClientRect();
        const cRect = canvas.getBoundingClientRect();
        const aX = aRect.left + aRect.width / 2 - cRect.left;
        const aY = aRect.top + aRect.height / 2 - cRect.top;
        const bX = bRect.left + bRect.width / 2 - cRect.left;
        const bY = bRect.top + bRect.height / 2 - cRect.top;

        ctx.strokeStyle = "hsl(195, 53%, 70%)";
        const R = 10;
        const D = 20;
        ctx.beginPath();
        if (Math.abs(aX - bX) < Math.abs(aY - bY)) {
            const trueR = Math.min(Math.abs(aX - bX) / 2, R);
            const sgn = aY < bY ? 1 : -1;
            const d = Math.min(D, Math.max(1, Math.abs(aY - bY) - aRect.height / 2 - bRect.height / 2 - trueR * 2));
            if (type === 0) {
                const yD = aY + sgn * (aRect.height / 2 + d / 2);

                ctx.moveTo(aX + D / 2, yD);
                ctx.lineTo(aX - D / 2, yD);
                createDiv(aX, yD, 12, idx);
            }
            if (type === 1) {
                const yD = aY + sgn * (aRect.height / 2 + d);

                ctx.moveTo(aX + D / 2, aY + sgn * (aRect.height / 2 - 2));
                ctx.lineTo(aX, yD);
                ctx.lineTo(aX - D / 2, aY + sgn * (aRect.height / 2 - 2));
                createDiv(aX, yD - sgn * 10, 12, idx);
            }
            ctx.moveTo(aX, aY);

            const midY = (aY + bY) / 2;
            let cY = midY > aY ? midY - trueR : midY + trueR;
            let cX = aX > bX ? aX - trueR : aX + trueR;
            ctx.lineTo(aX, cY);
            makeArc(ctx, cX, cY, aX < bX, aY < bY, trueR);
            ctx.moveTo(cX, midY);

            cX = aX > bX ? bX + trueR : bX - trueR;
            cY = midY > bY ? midY - trueR : midY + trueR;
            ctx.lineTo(cX, midY);
            makeArc(ctx, cX, cY, aX > bX, aY > bY, trueR);
            ctx.moveTo(bX, cY);
            ctx.lineTo(bX, bY);

        } else {
            const trueR = Math.min(Math.abs(aY - bY) / 2, R);

            const sgn = aX < bX ? 1 : -1;
            const d = Math.min(D, Math.max(1, Math.abs(aX - bX) - aRect.width / 2 - bRect.width / 2 - trueR * 2));

            if (type === 0) {
                const xD = aX + sgn * (aRect.width / 2 + d / 2);

                ctx.moveTo(xD, aY + D / 2);
                ctx.lineTo(xD, aY - D / 2);

                createDiv(xD, aY, 12, idx);
            }
            if (type === 1) {
                const xD = aX + sgn * (aRect.width / 2 + d);

                ctx.moveTo(aX + sgn * (aRect.width / 2 - 2), aY + D / 2);
                ctx.lineTo(xD, aY);
                ctx.lineTo(aX + sgn * (aRect.width / 2 - 2), aY - D / 2);
                createDiv(xD - sgn * 10, aY, 12, idx);
            }



            ctx.moveTo(aX, aY);
            const midX = (aX + bX) / 2;
            let cX = midX > aX ? midX - trueR : midX + trueR;
            let cY = aY > bY ? aY - trueR : aY + trueR;
            ctx.lineTo(cX, aY);
            makeArc(ctx, cX, cY, aX > bX, aY > bY, trueR);
            ctx.moveTo(midX, cY);

            cX = midX > bX ? midX - trueR : midX + trueR;
            cY = aY > bY ? bY + trueR : bY - trueR;
            ctx.lineTo(midX, cY);
            makeArc(ctx, cX, cY, aX < bX, aY < bY, trueR);
            ctx.moveTo(cX, bY);
            ctx.lineTo(bX, bY);
        }

        ctx.stroke();
    });
}

setInterval(renderConnections, 1000 / 60);

//only important things for backend
let elements = [];
let connections = [];
///

function convertToJSON() {
    const elementToTable = new Map();
    const relationshipsCovered = new Set();
    const tables = [];
    const relationships = [];
    for (const element of elements) {
        if (element.tagName !== "BDB-ENTITY") {
            continue;
        }
        const table = {
            name: element.title,
            columns: []
        };
        for (const connection of connections) {
            if (connection[0] === element) {
                if (connection[1].tagName === "BDB-ATTRIBUTE") {
                    table.columns.push({ name: connection[1].title, type: Number(connection[1].type) });
                }
            }
        }
        tables.push(table);
        elementToTable.set(element, tables.length - 1);
    }
    for (const connection of connections) {
        if (connection[1].tagName === "BDB-RELATIONSHIP"
            && !relationshipsCovered.has(connection[1])) {

            const relationship = {
                name: connection[1].title,
                tables: [],
                relationshipType: [],
            };
            for (const connection2 of connections) {
                if (connection2[1] === connection[1]) {
                    relationship.tables.push(elementToTable.get(connection2[0]));
                    relationship.relationshipType.push(connection2[2]);
                    relationshipsCovered.add(connection2[0]);
                }
            }
            relationships.push(relationship);
            relationshipsCovered.add(connection[1]);
        }
    }
    const json = {
        tables,
        relationships
    }
    return json;
}


const addEntity = (title) => {
    const entity = document.createElement("bdb-entity");
    entity.style.left = Math.random() * 80 + "%";
    entity.style.top = Math.random() * 80 + "%";
    canvasContainer.appendChild(entity);
    entity.title = title;

    addDragAndDrop(entity);
    elements.push(entity);
    addAttributeButton.classList.remove("disabled");
    deleteButton.classList.remove("disabled");
    if (elements.length > 1) {
        addRelationshipButton.classList.remove("disabled");
    }
}

const addRelationship = (title, a, b) => {
    const relationship = document.createElement("bdb-relationship");
    relationship.style.left = Math.random() * 80 + "%";
    relationship.style.top = Math.random() * 80 + "%";
    canvasContainer.appendChild(relationship);
    relationship.title = title;
    addDragAndDrop(relationship);
    elements.push(relationship);
    connections.push([a, relationship, 0]);
    connections.push([b, relationship, 0]);
}

const addAttribute = (title, element) => {
    const attribute = document.createElement("bdb-attribute");
    attribute.style.left = Math.random() * 80 + "%";
    attribute.style.top = Math.random() * 80 + "%";
    canvasContainer.appendChild(attribute);
    attribute.title = title;
    addDragAndDrop(attribute);
    elements.push(attribute);
    connections.push([element, attribute]);
}

const addEntityButton = document.getElementById("add-entity-button");
const addRelationshipButton = document.getElementById("add-relationship-button");
const addAttributeButton = document.getElementById("add-attribute-button");
const deleteButton = document.getElementById("delete-button");


addRelationshipButton.classList.add("disabled");
addAttributeButton.classList.add("disabled");
deleteButton.classList.add("disabled");

//DELETE
let deleting = false;

const removeFunction = (el) => {
    elements = elements.filter((element) => element !== el);
    el.remove();
    if (el.tagName === "BDB-ENTITY") {
        const connectionsWithEl = connections.filter((connection) => connection.includes(el));
        connectionsWithEl.forEach((connection) => {
            if (connection[0] !== el) {
                removeFunction(connection[0]);
            }
            if (connection[1] !== el) {
                removeFunction(connection[1]);
            }

        });
    }
    connections = connections.filter((connection) => connection[0] !== el && connection[1] !== el);
    if (elements.length === 0) {
        addAttributeButton.classList.add("disabled");
        deleteButton.classList.add("disabled");
    }
    if (elements.length < 2) {
        addRelationshipButton.classList.add("disabled");
    }

}
deleteStart = () => {
    if (elements.length === 0) {
        return;
    }
    deleting = true;
    deleteButton.textContent = "Cancel";
    deleteButton.classList.add("cancel");
    deleteButton.classList.remove("delete");


    elements.forEach((element) => {
        element.style.border = "1px solid red";
        element.classList.add("selectable");
        element.removeF = () => removeFunction(element)
        element.addEventListener("click", element.removeF)
    });
}

deleteEnd = () => {
    deleteButton.textContent = "Delete";
    deleteButton.classList.remove("cancel");
    deleteButton.classList.add("delete");
    elements.forEach((element) => {
        element.style.border = "";
        element.classList.remove("selectable");
        element.removeEventListener("click", element.removeF)
    });
    deleting = false;
}

/////////////////////
//ATTRIBUTE

let selectingEntityForAttribute = false;
attributeStart = () => {
    if (elements.length === 0) {
        return;
    }
    addAttributeButton.textContent = "Cancel";
    addAttributeButton.classList.add("cancel");
    addAttributeButton.classList.remove("start");

    selectingEntityForAttribute = true;
    elements.forEach((element) => {
        if (element.tagName !== "BDB-ENTITY")
            return;
        element.style.border = "1px solid hsl(150, 100%, 50%)";
        element.classList.add("selectable");
        element.addA = () => {
            addAttribute("Attribute", element);
        }
        element.addEventListener("click", element.addA)
    });
}

attributeEnd = () => {
    addAttributeButton.textContent = "+ Attribute";
    addAttributeButton.classList.remove("cancel");
    addAttributeButton.classList.add("start");

    selectingEntityForAttribute = false;
    elements.forEach((element) => {
        element.style.border = "";
        element.classList.remove("selectable");
        element.removeEventListener("click", element.addA)
    });
}



let selectingEntitiesForRelationship = false;
const entitiesToConnect = [];
const relationshipStart = () => {
    if (elements.length < 2) {
        return;
    }

    selectingEntitiesForRelationship = true;
    addRelationshipButton.textContent = "Cancel";
    addRelationshipButton.classList.add("cancel");
    addRelationshipButton.classList.remove("start");

    elements.forEach((element) => {
        if (element.tagName !== "BDB-ENTITY")
            return;
        element.style.border = "1px solid hsl(50, 100%, 50%)";
        element.classList.add("selectable");
        element.addR = () => {
            if (entitiesToConnect.includes(element)) {
                element.selected = false;
                entitiesToConnect.splice(0);
                return;
            }
            entitiesToConnect.push(element);
            element.selected = true;
            if (entitiesToConnect.length === 2) {
                addRelationship("Relationship", entitiesToConnect[0], entitiesToConnect[1]);
                entitiesToConnect[0].selected = false;
                entitiesToConnect[1].selected = false;
                entitiesToConnect.length = 0;
            }
        }
        element.addEventListener("click", element.addR)
    });
}

const relationshipEnd = () => {
    addRelationshipButton.textContent = "+ Relationship";
    addRelationshipButton.classList.remove("cancel");
    addRelationshipButton.classList.add("start");

    elements.forEach((element) => {
        element.style.border = "";
        element.classList.remove("selectable");
        element.removeEventListener("click", element.addR)
        element.selected = false;
    });
    selectingEntitiesForRelationship = false;
    entitiesToConnect.length = 0;
}


deleteButton.addEventListener("click", () => {
    if (selectingEntityForAttribute) {
        attributeEnd();
    }
    if (selectingEntitiesForRelationship) {
        relationshipEnd();
    }
    if (deleting) {
        deleteEnd();
    } else {
        deleteStart();
    }
});

addAttributeButton.addEventListener("click", () => {
    if (deleting) {
        deleteEnd();
    }
    if (selectingEntitiesForRelationship) {
        relationshipEnd();
    }
    if (selectingEntityForAttribute) {
        attributeEnd();
    } else {
        attributeStart();
    }
});

addEntityButton.addEventListener("click", () => {
    if (deleting) {
        deleteEnd();
        deleting = false;
    }
    if (selectingEntityForAttribute) {
        attributeEnd();
    }
    if (selectingEntitiesForRelationship) {
        relationshipEnd();
    }
    addEntity("Entity");

});

addRelationshipButton.addEventListener("click", () => {
    if (deleting) {
        deleteEnd();
    }

    if (selectingEntityForAttribute) {
        attributeEnd();
    }
    if (selectingEntitiesForRelationship) {
        relationshipEnd();
    } else {
        relationshipStart();
    }
});

//DRAG AND DROP
const addDragAndDrop = (element) => {
    let rX = 0;
    let rY = 0;
    let grabbing = false;
    const canBeGrabbed = () => {

        if (element.classList.contains("editing")) {
            return false;
        }
        if (deleting) {
            return false;
        }
        if (selectingEntityForAttribute || selectingEntitiesForRelationship) {
            if (element.tagName === "BDB-ENTITY") {

                return false;
            }
        }
        return true;
    }
    element.addEventListener("mousedown", (event) => {
        if (!canBeGrabbed()) {
            return;
        }
        rX = element.offsetLeft - event.clientX;
        rY = element.offsetTop - event.clientY;
        grabbing = true;
    });

    document.addEventListener("mouseup", () => {
        element.grabbing = false;
        grabbing = false;
    });

    document.addEventListener("mousemove", (ev) => {
        if (!canBeGrabbed()) {
            return;
        }
        if (ev.buttons === 1 && grabbing) {

            const clippedX = Math.max(
                Math.min(
                    ev.clientX,
                    canvasContainer.clientWidth - element.offsetWidth - rX
                ),
                -rX
            );
            const clippedY = Math.max(
                Math.min(
                    ev.clientY,
                    canvasContainer.clientHeight - element.offsetHeight - rY
                ),
                -rY
            );
            const cX = `${(100 * (clippedX + rX)) / canvasContainer.clientWidth
                }%`;
            const cY = `${(100 * (clippedY + rY)) / canvasContainer.clientHeight
                }%`;

            element.style.left = cX;
            element.style.top = cY;
            element.grabbing = true;
            renderConnections();

        }
    }
    );
}

const generateButton = document.getElementById("generate-button");
const modal = document.getElementById("result-modal");
const tableContainer = document.getElementById("table-inner-container");
const tableName = document.getElementById("table-name");
const closeButton = document.getElementById("close-button");
const nextButton = document.getElementById("next-button");
const previousButton = document.getElementById("prev-button");
const tableCounter = document.getElementById("table-counter");
let prevFn = () => { };
let nextFn = () => { };
closeButton.addEventListener("click", closeModal);
function closeModal() {
    modal.style.display = "none";
    nextButton.removeEventListener("click", nextFn);
    previousButton.removeEventListener("click", prevFn);

}
closeModal();
function openModal() {
    modal.style.display = "flex";
}
generateButton.addEventListener("click", () => {
    const requestData = convertToJSON();

    openModal();
    let dots = ""
    tableContainer.innerHTML = `<div id = "loading"> Loading${dots}</div>`;
    interval = setInterval(() => {
        if (dots.length === 7) {
            dots = "";
        }
        else {
            dots += ".";
        }
        tableContainer.innerHTML = `<div id = "loading"> Loading${dots}</div>`;
    }, 500);
    tableCounter.textContent = "0/0";
    tableName.textContent = "";

    fetch("http://localhost:5000/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
    })
        .then(response => response.json())
        .then(jsonData => {
            clearInterval(interval);
            // Handle the response data
            const data = []
            const names = []
            jsonData.forEach((tableJSON) => {
                data.push(JSON.parse(tableJSON[0]));
                names.push(tableJSON[1]);
            });
            let currentTable = 0;
            tableCounter.textContent = "1/" + data.length;
            tableName.textContent = names[currentTable];

            nextFn = () => {
                currentTable = (currentTable + 1) % data.length;
                tableCounter.textContent = (currentTable + 1) + "/" + data.length;
                tableName.textContent = names[currentTable];
                tableContainer.innerHTML = '';
                displayTable(data[currentTable]);
            };
            prevFn = () => {
                currentTable = (currentTable - 1 + data.length) % data.length;
                tableCounter.textContent = (currentTable + 1) + "/" + data.length;
                tableName.textContent = names[currentTable];
                tableContainer.innerHTML = '';
                displayTable(data[currentTable]);
            };
            nextButton.addEventListener("click", nextFn);
            previousButton.addEventListener("click", prevFn);

            openModal();

            // Function to generate and display the table
            function displayTable(data) {
                // Extract headers (keys of the object)
                const headers = Object.keys(data);

                // Determine the number of rows by looking at the length of the first key
                const numRows = Object.keys(data[headers[0]]).length;

                // Create the table element
                const table = document.createElement('table');

                // Create table header row
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                headers.forEach(header => {
                    const th = document.createElement('th');
                    th.textContent = header;
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);

                // Create table body
                const tbody = document.createElement('tbody');
                for (let i = 0; i < numRows; i++) {
                    const row = document.createElement('tr');
                    headers.forEach(header => {
                        const td = document.createElement('td');
                        td.textContent = data[header][i]; // Access the specific cell
                        row.appendChild(td);
                    });
                    tbody.appendChild(row);
                }
                table.appendChild(tbody);

                // Append the table to the container
                tableContainer.appendChild(table);
            }
            function jsonToCsv(json) {
                const headers = Object.keys(json); // Extract headers
                const numRows = Object.keys(json[headers[0]]).length; // Determine the number of rows

                // Create CSV content
                let csvContent = headers.join(",") + "\n"; // Add headers to CSV

                // Loop through rows
                for (let i = 0; i < numRows; i++) {
                    const row = headers.map(header => json[header][i]); // Extract each row
                    csvContent += row.join(",") + "\n"; // Add row to CSV
                }

                return csvContent;
            }

            // Function to download the CSV file
            function downloadCsv(filename, csvContent) {
                const blob = new Blob([csvContent], { type: 'text/csv' }); // Create a Blob
                const url = URL.createObjectURL(blob); // Create a URL for the Blob
                const a = document.createElement('a'); // Create a link element
                a.href = url;
                a.download = filename; // Set the filename
                a.click(); // Programmatically click the link to start download
                URL.revokeObjectURL(url); // Clean up the URL object
            }

            // Add event listener to the button
            document.getElementById("download-csv").addEventListener("click", () => {
                data.forEach((table, idx) => {
                    const csvContent = jsonToCsv(table);
                    downloadCsv(`${names[idx]}.csv`, csvContent);
                });
            });

            // Call the function with the response data

            tableContainer.innerHTML = ''; // Clear previous content
            displayTable(data[currentTable]); // Display the first table

        })
        .catch(error => {
            clearInterval(interval);
            // Handle the error
            console.error(error);

            tableContainer.innerHTML = `<div id = "error"> Error: ${error.message}</div>`;
        });
});
