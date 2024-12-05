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

  get type() {
    return this.getAttribute('type');
  }

  set type(value) {
    this.setAttribute('type', value);
  }

  static get observedAttributes() {
    return ['title', 'grabbing', 'type'];
  }
  connectedCallback() {
    const shadow = this.attachShadow({ mode: 'open' });
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
      <div id = "outer"><div id = "inner">${this.getAttribute('title')}</div>
        <select name="type" id="type">
          <option value="1">STRING</option>
          <option value="2">INTEGER</option>
          <option value="3">FLOAT</option>
          <option value="4">BOOLEAN</option>
          <option value="5">DATE</option>
          <option value="6">TIME</option>
          <option value="7">DATETIME</option>
          <option value="8">BINARY</option>
        </select>
      </div>
    `;
    this.type = 1;
    const select = wrapper.querySelector('#type')
    select.addEventListener('change', () => {
      this.type = select.value
    });

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
      const div = this.shadowRoot.querySelector("#inner")
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
        const par = input.parentElement
        par.removeChild(input)
        par.insertBefore(div, par.firstChild)
        this.classList.remove("editing")
        this.title = value
      })
      const par = div.parentElement
      par.removeChild(div)
      par.insertBefore(input, par.firstChild)
      this.classList.add("editing")

      input.focus()

      input.selectionStart = input.selectionEnd = 10000
    })
    this.shadowRoot.querySelector('#inner').textContent = this.title;
    this.grabbing
  }
  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'title') {
      this.shadowRoot.querySelector('#inner').textContent = newValue;
    }
    if (name === 'grabbing') {
      if (newValue === 'true') {
        this.shadowRoot.querySelector('#inner')?.classList.add('grabbing');
      } else {
        this.shadowRoot.querySelector('#inner')?.classList.remove('grabbing');
      }
    }
    console.log(name, oldValue, newValue)

    // Handle other attributes if needed
  }

}
