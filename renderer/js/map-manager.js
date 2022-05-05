var API_BASE_URL = "http://127.0.0.1:5000/v1";

class MapManager {
    constructor() {
        this.pixi = new PIXI.Application({ width:  window.innerWidth, height:  window.innerHeight });
        this.timer = null;
        
        this.map_objects = [];

        document.body.appendChild(this.pixi.view);

        this.pixi.ticker.add((dlt) => this.loop(dlt));

        this.cumulative_delta = 0.0;

        this.delta_map_obj_idx = 0;



    }

    start()
    {
        // get all objects
        var me = this;
        fetch(`${API_BASE_URL}/objects/`).then(response => response.json()).then(function(data)
        {
            for (const obj of data)
            {
                
                switch(obj.type)
                {
                    case "defender": {
                        var item = new MapItem(obj.id, "/assets/PNG/Tanks/tankBlue.png");
                        me.map_objects.push(item);
                        me.pixi.stage.addChild(item.sprite);
                        break;
                    }

                    case "attacker": {
                        var item = new MapItem(obj.id, "/assets/PNG/Tanks/tankRed.png");
                        me.map_objects.push(item);
                        me.pixi.stage.addChild(item.sprite);
                        break;
                    }

                    case "target": {
                        var item = new MapItem(obj.id, "/assets/PNG/Obstacles/barrelRed_up.png");
                        me.map_objects.push(item);
                        me.pixi.stage.addChild(item.sprite);
                        break;
                    }

                    case "obstacle": {
                        var item = new MapItem(obj.id, "/assets/PNG/Obstacles/sandbagBrown.png");
                        me.map_objects.push(item);
                        me.pixi.stage.addChild(item.sprite);
                        break;
                    }

                }
                
                

            }


            
        });       

    }


    loop(delta)
    {
        
        this.cumulative_delta += delta;

        if(this.cumulative_delta < 5)return;

        if(this.map_objects.length != 0)
        {
            this.map_objects[this.delta_map_obj_idx].update();
            this.delta_map_obj_idx += 1;
        }

            
        if(this.delta_map_obj_idx >= this.map_objects.length)this.delta_map_obj_idx = 0;
            
        
        this.cumulative_delta = 0;

    }


};
