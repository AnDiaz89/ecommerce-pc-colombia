/* Lógica de la tienda (Alpine.js) para PC Forge Colombia */

function tienda() {
    return {
        apiDisponible: false,
        mensajeEstado: "Comprobando API...",
        productos: [],
        categorias: [],
        categoriaSeleccionada: null,
        cargandoProductos: true,
        errorProductos: "",
        notificacion: "",
        temporizadorNotificacion: null,
        carrito: [],
        carritoAbierto: false,
        formularioIA: {
            presupuesto: 4000000,
            necesidad: "gaming",
            descripcion: "",
            resolucion: "1080p",
            juegosTexto: "Valorant, Fortnite, Warzone",
        },
        procesandoIA: false,
        errorIA: "",
        recomendacionIA: null,

        async inicializar() {
            this.cargarCarritoLocal();
            await this.comprobarApi();
            await this.cargarCategorias();
            await this.cargarProductos();
        },

        async comprobarApi() {
            this.apiDisponible = false;
            this.mensajeEstado = "Comprobando API...";

            try {
                const respuesta = await fetch("/health");

                if (!respuesta.ok) {
                    throw new Error("Respuesta no válida");
                }

                this.apiDisponible = true;
                this.mensajeEstado = "API conectada";
            } catch (error) {
                this.apiDisponible = false;
                this.mensajeEstado = "API no disponible";
            }
        },

        async cargarCategorias() {
            try {
                const respuesta = await fetch("/categorias");

                if (!respuesta.ok) {
                    throw new Error("No fue posible cargar categorías");
                }

                this.categorias = await respuesta.json();
            } catch (error) {
                this.categorias = [];
            }
        },

        async cargarProductos() {
            this.cargandoProductos = true;
            this.errorProductos = "";

            try {
                const parametros = new URLSearchParams({
                    solo_activos: "true",
                });

                if (this.categoriaSeleccionada !== null) {
                    parametros.set(
                        "categoria_id",
                        String(this.categoriaSeleccionada)
                    );
                }

                const url = "/productos?" + parametros.toString();

                const respuesta = await fetch(url);

                if (!respuesta.ok) {
                    throw new Error("No fue posible cargar");
                }

                this.productos = await respuesta.json();
            } catch (error) {
                this.errorProductos = "No pudimos cargar los productos.";
            } finally {
                this.cargandoProductos = false;
            }
        },

        async seleccionarCategoria(categoriaId) {
            this.categoriaSeleccionada = categoriaId;

            await this.cargarProductos();
        },

        confirmarProducto(producto) {
            if (producto.stock < 1) {
                this.mostrarNotificacion(
                    "Este producto no tiene stock disponible"
                );
                return;
            }

            const itemExistente = this.carrito.find(
                (item) => item.id === producto.id
            );

            if (itemExistente) {
                if (itemExistente.cantidad >= producto.stock) {
                    this.mostrarNotificacion(
                        "No puedes superar el stock disponible"
                    );
                    return;
                }

                itemExistente.cantidad += 1;
            } else {
                this.carrito.push({
                    id: producto.id,
                    nombre: producto.nombre,
                    precio: Number(producto.precio),
                    stock: producto.stock,
                    imagen_url: producto.imagen_url,
                    cantidad: 1,
                });
            }

            this.guardarCarritoLocal();

            this.mostrarNotificacion(
                producto.nombre + " añadido al carrito"
            );
        },

        mostrarNotificacion(mensaje) {
            this.notificacion = mensaje;

            clearTimeout(this.temporizadorNotificacion);

            this.temporizadorNotificacion = setTimeout(() => {
                this.notificacion = "";
            }, 2500);
        },

        guardarCarritoLocal() {
            localStorage.setItem(
                "pc-forge-carrito",
                JSON.stringify(this.carrito)
            );
        },

        cargarCarritoLocal() {
            try {
                const carritoGuardado = localStorage.getItem(
                    "pc-forge-carrito"
                );

                this.carrito = carritoGuardado
                    ? JSON.parse(carritoGuardado)
                    : [];
            } catch (error) {
                this.carrito = [];
            }
        },

        cantidadCarrito() {
            return this.carrito.reduce(
                (total, item) => total + item.cantidad,
                0
            );
        },

        totalCarrito() {
            return this.carrito.reduce((total, item) => {
                return total + item.precio * item.cantidad;
            }, 0);
        },

        aumentarCantidad(item) {
            if (item.cantidad >= item.stock) {
                this.mostrarNotificacion(
                    "No puedes superar el stock disponible"
                );
                return;
            }

            item.cantidad += 1;
            this.guardarCarritoLocal();
        },

        disminuirCantidad(item) {
            if (item.cantidad <= 1) {
                this.eliminarDelCarrito(item.id);
                return;
            }

            item.cantidad -= 1;
            this.guardarCarritoLocal();
        },

        eliminarDelCarrito(productoId) {
            this.carrito = this.carrito.filter(
                (item) => item.id !== productoId
            );

            this.guardarCarritoLocal();
            this.mostrarNotificacion("Producto eliminado del carrito");
        },

        async solicitarRecomendacion() {
            this.procesandoIA = true;
            this.errorIA = "";
            this.recomendacionIA = null;

            const juegos = this.formularioIA.juegosTexto
                .split(",")
                .map((juego) => juego.trim())
                .filter((juego) => juego.length > 0)
                .slice(0, 10);

            const solicitud = {
                presupuesto: Number(this.formularioIA.presupuesto),
                necesidad: this.formularioIA.necesidad,
                descripcion: this.formularioIA.descripcion,
                resolucion: this.formularioIA.resolucion,
                juegos: juegos,
            };

            try {
                const respuesta = await fetch(
                    "/ia/recomendar-ensamble",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(solicitud),
                    }
                );

                const datos = await respuesta.json();

                if (!respuesta.ok) {
                    throw new Error(
                        datos.detail ||
                            "No fue posible generar la recomendación"
                    );
                }

                this.recomendacionIA = datos;
            } catch (error) {
                this.errorIA = error.message;
            } finally {
                this.procesandoIA = false;
            }
        },

        formatearPrecio(valor) {
            return new Intl.NumberFormat("es-CO", {
                style: "currency",
                currency: "COP",
                maximumFractionDigits: 0,
            }).format(Number(valor));
        },
    };
}
