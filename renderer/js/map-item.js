var API_BASE_URL = "http://127.0.0.1:5000/v1";
var TO_RADIANS = Math.PI/180; 

class MapItem {

    constructor(uuid, img_path)
    {
        this.sprite = PIXI.Sprite.from(img_path);
        this.uuid = uuid;
        this.state = {};
        this.sprite.width = 20;
        this.sprite.height = 20;

    }


    update()
    {
        var me = this; /* stupid variable hoisting... */
        fetch(`${API_BASE_URL}/objects/id/${this.uuid}`).then(response => response.json()).then(function(data)
        {
            me.state = data;
            me.draw();
            
        });       

    }

    draw()
    {
        if(this.state.state == "active")
        {
            this.sprite.x = this.state.x;
            this.sprite.y = this.state.y;
            
        }

    }


    

}
