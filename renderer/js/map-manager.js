function doReset(api_base) {
    fetch(`${api_base}/commands/reset`, { method: "POST" }).then(function () {

        location.reload(true);

    });



}


class MapManager {
    constructor(host) {
        this.pixi = new PIXI.Application({ width: window.innerWidth, height: window.innerHeight, backgroundColor: 0x160d61 });

        this.api_base = `http://${host}/v1`;

        this.timer = null;

        this.map_objects = [];

        document.body.appendChild(this.pixi.view);

        this.pixi.ticker.minFPS = 4;
        this.pixi.ticker.maxFPS = 8;


        this.pixi.ticker.add((dlt) => this.loop(dlt));


        this.delta_map_obj_idx = 0;

        this.reset_button = new MapButton("/assets/buttons/reset-up.png", "/assets/buttons/reset-dn.png", window.innerWidth - 100, 100, () => doReset(this.api_base));

        this.pixi.stage.addChild(this.reset_button.sprite);



    }

    addToMapIfNotExists(mapitem) {
        for (const m of this.map_objects) {
            if (mapitem.uuid == m.uuid) {
                return;
            }
        }

        this.map_objects.push(mapitem);
        this.pixi.stage.addChild(mapitem.sprite);


    }

    load() {
        // get all objects
        var me = this;
        fetch(`${this.api_base}/objects/`).then(response => response.json()).then(function (data) {
            for (const obj of data) {

                switch (obj.type) {
                    case "defender": {
                        var tex_map = {
                            active: "/assets/space/defender01.png",
                            dead: "/assets/space/generic-dead.png"

                        };
                        var item = new MapItem(me.api_base, obj.id, tex_map);
                        me.addToMapIfNotExists(item);
                        break;
                    }

                    case "attacker": {
                        var tex_map = {
                            active: "/assets/space/attacker01.png",
                            dead: "/assets/space/generic-dead.png"

                        };
                        var item = new MapItem(me.api_base, obj.id, tex_map);
                        me.addToMapIfNotExists(item);
                        break;
                    }

                    case "target": {
                        var tex_map = {
                            active: "/assets/space/target01.png",
                            dead: "/assets/space/generic-dead.png"

                        };
                        var item = new MapItem(me.api_base, obj.id, tex_map);
                        me.addToMapIfNotExists(item);
                        break;
                    }

                    case "obstacle": {

                        var obstacle_types = [
                            {
                                active: "/assets/space/obstacle01.png",
                                dead: "/assets/space/generic-dead.png"

                            },
                            {
                                active: "/assets/space/obstacle02.png",
                                dead: "/assets/space/generic-dead.png"

                            }
                        ];
                        var item = new MapItem(me.api_base, obj.id, obstacle_types[Math.floor(Math.random() * obstacle_types.length)]);
                        me.addToMapIfNotExists(item);
                        break;
                    }

                }



            }



        });

    }


    loop(delta) {


        if (this.map_objects.length != 0) {
            if (this.map_objects[this.delta_map_obj_idx].update() == false) {
                this.map_objects.splice(this.delta_map_obj_idx, 1);
            }
            this.delta_map_obj_idx += 1;
        }


        if (this.delta_map_obj_idx >= this.map_objects.length) {
            this.delta_map_obj_idx = 0;
            this.load();
        }



    }


};
