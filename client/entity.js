export class Entity extends HTMLElement {
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

  get selected() {
    return this.getAttribute('selected');
  }

  set selected(value) {
    this.setAttribute('selected', value);
  }

  get grabbing() {
    return this.getAttribute('grabbing');
  }

  set grabbing(value) {
    this.setAttribute('grabbing', value);
  }
  static get observedAttributes() {
    return ['title', 'selected', 'grabbing'];
  }
  connectedCallback() {
    this.rx = 0;
    this.ry = 0;

    const shadow = this.attachShadow({ mode: 'open' });
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
      <div>${this.getAttribute('title')}</div>
    `;

    // Fetch and apply the external CSS
    fetch('entity.css')
      .then(response => response.text())
      .then(css => {
        const style = document.createElement('style');
        style.textContent = css;
        shadow.appendChild(style);
      });

    shadow.appendChild(wrapper);
    this.addEventListener("dblclick", () => {
      if (this.classList.contains("editing")) {
        return;
      }
      const div = this.shadowRoot.querySelector("div")
      const input = document.createElement('input')
      input.value = div.textContent
      input.style.left = div.style.left
      input.style.top = div.style.top
      const f = () => {
        input.style.width = ((input.value.length)) + 'ch';
      }
      f()
      input.addEventListener("input", f)
      input.addEventListener("keypress", (ev) => {
        if (ev.key === "Enter") {
          input.blur()
        }
      })
      input.addEventListener("blur", () => {
        const value = input.value
        this.shadowRoot.removeChild(input)
        this.shadowRoot.appendChild(div)
        this.classList.remove("editing")
        this.title = value
      })
      this.shadowRoot.removeChild(div)
      this.shadowRoot.appendChild(input)
      this.classList.add("editing")
      input.focus()

      input.selectionStart = input.selectionEnd = 10000
    })

    this.grabbing = false;
    this.selected = false;
  }
  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'title') {
      this.shadowRoot.querySelector('div').textContent = newValue;
    }
    if (name === 'selected') {
      if (newValue === 'true') {
        this.shadowRoot.querySelector('div')?.classList.add('selected');
      } else {
        this.shadowRoot.querySelector('div')?.classList.remove('selected');
      }
    }
    if (name === 'grabbing') {
      if (newValue === 'true') {
        this.shadowRoot.querySelector('div')?.classList.add('grabbing');
      } else {
        this.shadowRoot.querySelector('div')?.classList.remove('grabbing');
      }
    }
    // Handle other attributes if needed
  }

}
