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
