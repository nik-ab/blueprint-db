export class Attribute extends HTMLElement {
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
      <div>${this.getAttribute('title')}</div>
    `;

    // Fetch and apply the external CSS
    fetch('attribute.css')
      .then(response => response.text())
      .then(css => {
        const style = document.createElement('style');
        style.textContent = css;
        shadow.appendChild(style);
      });

    shadow.appendChild(wrapper);
    this.addEventListener("dblclick", () => {
      const div = this.shadowRoot.querySelector("div")
      const input = document.createElement('input')
      input.value = div.textContent
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
        div.textContent = value
      })
      this.shadowRoot.removeChild(div)
      this.shadowRoot.appendChild(input)
      this.classList.add("editing")

      input.focus()

      input.selectionStart = input.selectionEnd = 10000
    })
    this.shadowRoot.querySelector('div').textContent = this.title;
    this.grabbing
  }
  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'title') {
      this.shadowRoot.querySelector('div').textContent = newValue;
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
