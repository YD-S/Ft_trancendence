export default class Paddle {
    constructor(PaddleElement, id) {
        this.id = id;
        this.PaddleElement = PaddleElement;
        this.reset();
    }

    get position() {
        return parseFloat(getComputedStyle(this.PaddleElement).getPropertyValue('--pos'));
    }

    set position(value) {
        this.PaddleElement.style.setProperty('--pos', value);
    }

    get heightPaddle() {
        return parseFloat(getComputedStyle(this.PaddleElement).getPropertyValue(`--paddle${this.id}_height`));
    }

    set heightPaddle(value) {
        this.PaddleElement.style.setProperty(`--paddle${this.id}_height`, value);
    }

    rect() {
        return this.PaddleElement.getBoundingClientRect();
    }

    update() {
        if(this.position < 0) this.position = 0;
        if(this.position > 100) this.position = 100;
    }

    reset() {
        this.position = 50;
    }
}