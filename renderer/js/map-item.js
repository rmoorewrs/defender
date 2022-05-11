var TO_RADIANS = Math.PI/180; 
var SPRITE_BASE_DIM_PX = 10;

class MapItem {

    /*
        api_base:       this should be something like 'http://host:port/v1'
        uuid:           object id
        texture_map:    a map/dict/object mapping state to texture image, for example {active: path/to/active.png, dead: path/to/dead.png, dying: path/to/dying.png}
        
   */
    constructor(api_base, uuid, texture_map)
    {
        this.textures = {};

        for(const state in texture_map)
        {
            this.textures[state] = PIXI.Texture.from(texture_map[state]);
        }

        
        this.sprite = PIXI.Sprite.from(this.textures.active);
        this.uuid = uuid;
        this.state = {};
        this.sprite.width = SPRITE_BASE_DIM_PX*2;
        this.sprite.height = SPRITE_BASE_DIM_PX*2;
        this.sprite.anchor.set(0.5); // set anchor to 50% so rotations occur around the center
        this.api_base = api_base;
    }


    update()
    {
        var me = this; /* stupid variable hoisting... */
        fetch(`${this.api_base}/objects/id/${this.uuid}`).then(response => response.json()).then(function(data)
        {
            me.state = data;
            return me.draw();
            
        });       

    }

    draw()
    {

        this.sprite.x = this.state.x;
        this.sprite.y = this.state.y;
        this.sprite.width = SPRITE_BASE_DIM_PX*this.state.radius;
        this.sprite.height = SPRITE_BASE_DIM_PX*this.state.radius;
        this.sprite.angle = this.state.rotation;
        
        // only change texture if we have a state-texture relationship
        if (this.state.state in this.textures)
        {
            this.sprite.texture = this.textures[this.state.state];
        }        


    }


    

}
