export class Relationship extends HTMLElement {
    constructor() {
        super();
    }
    // Define a property 'title'
    get title() {
        return this.getAttribute('title');
    }

    set title(value) {
        this.setAttribute('title', value);
    }

    get grabbing() {
        return this.getAttribute('grabbing');
    }

    set grabbing(value) {
        this.setAttribute('grabbing', value);
    }

    static get observedAttributes() {
        return ['title', 'grabbing'];
    }

    connectedCallback() {
        const shadow = this.attachShadow({ mode: 'open' });
        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
      <div class = "container"><div></div></div>
    `;

        // Fetch and apply the external CSS
        fetch('relationship.css')
            .then(response => response.text())
            .then(css => {
                const style = document.createElement('style');
                style.textContent = css;
                shadow.appendChild(style);
            });
        this.f = () => {
            let el = this.shadowRoot.querySelector(".container div")
            let l;
            if (!el) {
                el = this.shadowRoot.querySelector(".container input")
                l = el.value.length
            }
            else {

                l = el.textContent.length
            }
            el.style.width = (l) + 'ch';
            el.style.paddingLeft = ((l) / 5 + 1) + 'ch';
            el.style.paddingRight = ((l) / 5 + 1) + 'ch';

        }
        shadow.appendChild(wrapper);
        this.f();
        this.addEventListener("dblclick", () => {
            const container = this.shadowRoot.querySelector(".container")
            const div = this.shadowRoot.querySelector(".container div")
            const input = document.createElement('input')
            input.value = div.textContent

            this.f();
            input.addEventListener("input", this.f)
            input.addEventListener("keypress", (ev) => {
                if (ev.key === "Enter") {
                    input.blur()
                }
            })
            input.addEventListener("blur", (ev) => {
                const value = input.value
                container.removeChild(input)
                container.appendChild(div)
                this.classList.remove("editing")
                this.title = value

                this.f();
            })
            container.removeChild(div)
            container.appendChild(input)
            this.classList.add("editing")

            this.f();
            input.focus()

            input.selectionStart = input.selectionEnd = 10000
        })
        this.shadowRoot.querySelector('.container div').textContent = this.title;
        this.f();
        this.grabbing = false;
    }
    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'title') {
            this.shadowRoot.querySelector('.container div').textContent = newValue;
            this.f();
        }
        if (name === 'grabbing') {
            if (newValue === 'true') {
                this.shadowRoot.querySelector('.container div')?.classList.add('grabbing');
            } else {
                this.shadowRoot.querySelector('.container div')?.classList.remove('grabbing');
            }
        }
        // Handle other attributes if needed
    }

}
