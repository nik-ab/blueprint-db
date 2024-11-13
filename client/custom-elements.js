import { Entity } from "./entity.js";
import { Relationship } from "./relationship.js";
import { Attribute } from "./attribute.js";

customElements.define('bdb-entity', Entity);
customElements.define('bdb-relationship', Relationship);
customElements.define('bdb-attribute', Attribute);