var API_BASE_URL = "http://127.0.0.1:5000/v1";

class MapManager {
    constructor() {
        this.pixi = new PIXI.Application({ width:  window.innerWidth, height:  window.innerHeight, backgroundColor:0x479d2e });
        this.timer = null;
        
        this.map_objects = [];

        document.body.appendChild(this.pixi.view);

        this.pixi.ticker.add((dlt) => this.loop(dlt));

        this.cumulative_delta = 0.0;

        this.delta_map_obj_idx = 0;



    }

    addToMapIfNotExists(mapitem)
    {
        for(const m of this.map_objects)
        {
            if (mapitem.uuid == m.uuid)
            {
                return;
            }
        }
        
        this.map_objects.push(mapitem);
        this.pixi.stage.addChild(mapitem.sprite);
        

    }

    load()
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
                        var item = new MapItem(obj.id, "/assets/tanks/sherman.png");
                        me.addToMapIfNotExists(item);
                        break;
                    }

                    case "attacker": {
                        var item = new MapItem(obj.id, "/assets/tanks/panzer.png");
                        me.addToMapIfNotExists(item);
                        break;
                    }

                    case "target": {
                        var item = new MapItem(obj.id, "/assets/base/Sculptures/Sculpture-2.png");
                        me.addToMapIfNotExists(item);
                        break;
                    }

                    case "obstacle": {
                        var obstacle_types = [
                            "/assets/base/Stones/Stone-1.png",
                            "/assets/base/Stones/Stone-2.png",
                            "/assets/base/Trees/Tree-1/Tree-1-1.png",
                            "/assets/base/Trees/Tree-1/Tree-1-2.png",
                            "/assets/base/Trees/Tree-1/Tree-1-3.png",
                            "/assets/base/Trees/Tree-2/Tree-2-1.png",
                            "/assets/base/Trees/Tree-2/Tree-2-2.png",
                            "/assets/base/Trees/Tree-2/Tree-2-3.png"
            
                        ];
                        var item = new MapItem(obj.id, obstacle_types[Math.floor(Math.random() * obstacle_types.length)]);
                        me.addToMapIfNotExists(item);
                        break;
                    }

                }
                
                

            }


            
        });       

    }


    loop(delta)
    {
        
        this.cumulative_delta += delta;

        if(this.cumulative_delta < 1)return;

        if(this.map_objects.length != 0)
        {
            if(this.map_objects[this.delta_map_obj_idx].update() == false)
            {
                this.map_objects.splice(this.delta_map_obj_idx, 1);
            }
            this.delta_map_obj_idx += 1;
        }

            
        if(this.delta_map_obj_idx >= this.map_objects.length)
        {
            this.delta_map_obj_idx = 0;
            this.load();
        }            
        
        this.cumulative_delta = 0;

    }


};
