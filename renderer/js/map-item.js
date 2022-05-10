var API_BASE_URL = "http://127.0.0.1:5000/v1";
var TO_RADIANS = Math.PI/180; 
var SPRITE_BASE_DIM_PX = 10;

class MapItem {

    constructor(uuid, img_path)
    {
        this.sprite = PIXI.Sprite.from(img_path);
        this.uuid = uuid;
        this.state = {};
        this.sprite.width = SPRITE_BASE_DIM_PX*2;
        this.sprite.height = SPRITE_BASE_DIM_PX*2;
        this.sprite.anchor.set(0.5); // set anchor to 50% so rotations occur around the center

    }


    update()
    {
        var me = this; /* stupid variable hoisting... */
        fetch(`${API_BASE_URL}/objects/id/${this.uuid}`).then(response => response.json()).then(function(data)
        {
            me.state = data;
            return me.draw();
            
        });       

    }

    draw()
    {
        if(this.state.state == "active")
        {
            this.sprite.x = this.state.x;
            this.sprite.y = this.state.y;
            this.sprite.width = SPRITE_BASE_DIM_PX*this.state.radius;
            this.sprite.height = SPRITE_BASE_DIM_PX*this.state.radius;
            this.sprite.angle = this.state.rotation;
            return true;
            
        }
        else
        {

            this.sprite.destroy();
            return false;
        }

    }


    

}
