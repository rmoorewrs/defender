

class MapButton {

    constructor(btnUpImage, btnDownImage, x, y, onClick) {

        this.txt_up = PIXI.Texture.from(btnUpImage);
        this.txt_down = PIXI.Texture.from(btnDownImage);
        this.sprite = PIXI.Sprite.from(this.txt_up);
        this.sprite.width = 50;
        this.sprite.height = 50;
        this.sprite.anchor.set(0.5); // set anchor to 50% so rotations occur around the center
        this.sprite.x = x;
        this.sprite.y = y;
        this.on_click = onClick;
        this.sprite.buttonMode = true;
        this.sprite.interactive = true;
        this.sprite.on('pointerdown', () => this.buttonDown());
        this.sprite.on('pointerup', () => this.buttonUp());

    }

    click() {
        this.on_click();
    }


    buttonDown() {
        this.sprite.texture = this.txt_down;
        this.sprite.alpha = 1.0;

    }

    buttonUp() {
        this.sprite.texture = this.txt_up;
        this.click();
    }




}
