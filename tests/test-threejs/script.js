// Function to load and parse the JSON file
async function loadPolygons() {
    try {
      const response = await fetch('eiffelTower.json');  // Path to your JSON file
      if (!response.ok) {
        throw new Error('Failed to fetch JSON file');
      }

      const data = await response.json();
      console.log('Loaded JSON data:', data);  // Log the loaded data
      return data.geometries;  // Extract the geometries array

    } catch (error) {
      console.error('Error loading JSON:', error);  // Log any error
      return [];  // Return an empty array in case of error
    }
  }

  // Function to create a Three.js scene with extruded polygons
  async function createScene() {
    // Set up the scene, camera, and renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Set the near and far clipping planes (adjustable range)
    camera.near = 0.1; // The near clipping plane (distance from the camera)
    camera.far = 10000; // The far clipping plane (maximum view distance)
    camera.updateProjectionMatrix();  // Update the projection matrix after modifying the near and far planes

    // Add OrbitControls to allow the user to interact with the scene
    const controls = new THREE.OrbitControls(camera, renderer.domElement);

    // Load polygons from JSON
    const geometries = await loadPolygons();

    // Create the ground plane (flat surface)
    const planeGeometry = new THREE.PlaneGeometry(2000, 2000); // Size of the plane (adjustable)
    const planeMaterial = new THREE.MeshBasicMaterial({ color: 0xaaaaaa, side: THREE.DoubleSide });
    const plane = new THREE.Mesh(planeGeometry, planeMaterial);
    //plane.rotation.x = -Math.PI / 2; // Rotate the plane to lie flat on the X-Y plane
    scene.add(plane);

    // axis helper
    const axisHelper = new THREE.AxesHelper(100);  // Helper size is 10 units
    scene.add(axisHelper);

    // Loop through the polygons and add them to the scene
    geometries.forEach(polygon => {
      const [coords, height] = polygon;

        // Get x and y arrays 
        const x_coords = coords.x 
        const y_coords = coords.y 

        // Create a new shape from the polygon coordinates
        const shape = new THREE.Shape();

        for (let i = 0; i < x_coords.length; i++) {

            // Get x,y coords 
            const x = x_coords[i] 
            const y = y_coords[i] 

            if (i === 0) {
                shape.moveTo(x,y);  // Start the shape at the first point
                } else {
                shape.lineTo(x,y);  // Connect to the next point
                }
        }

        shape.closePath();  // Close the path to form the polygon

        // Extrude the shape into 3D
        const extrudeSettings = {
            depth: height,  // Use the height from the JSON data
            bevelEnabled: false
        };

        const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        const material = new THREE.MeshBasicMaterial({ color: 0x054564, side: THREE.DoubleSide });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(0, 0, 0);  // Center the mesh (optional)
        scene.add(mesh);
    });

    // Create a basic scene (add objects, lights, etc.)
    /*const material_sphere = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    const geometry = new THREE.SphereGeometry(100, 320, 320);
    const sphere = new THREE.Mesh(geometry, material_sphere);
    scene.add(sphere);*/

    // test 
    const length = 12, width = 8;
    const shape = new THREE.Shape();
    shape.moveTo( 0,0 );
    shape.lineTo( 0, width );
    shape.lineTo( length, width );
    shape.lineTo( length, 0 );
    shape.lineTo( 0, 0 );

    const extrudeSettings = {
        depth: 16,
        bevelEnabled: false
    };

    const geometry = new THREE.ExtrudeGeometry( shape, extrudeSettings );
    const material_debug = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
    const mesh = new THREE.Mesh( geometry, material_debug ) ;
    scene.add( mesh );

    // Adjust camera position
    camera.position.set(0, 1000, 300);  // Set a better initial camera position
    camera.lookAt(0, 0, 0);  // Ensure the camera is looking at the center

    // Animation loop
    function animate() {
      requestAnimationFrame(animate);
      controls.update(); // Update controls
      renderer.render(scene, camera);
    }
    animate();
  }

  // Start the scene creation
  createScene();