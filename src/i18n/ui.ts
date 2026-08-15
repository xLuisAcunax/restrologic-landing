/**
 * RestroLogic — translation dictionary.
 *
 * Contract: every locale MUST declare the exact same key set. `TranslationKey`
 * is derived from the default locale, and each locale is checked against it at
 * compile time, so a missing or misspelt key is a build error rather than a
 * silent fallback at runtime.
 */

export const languages = {
  es: 'Español',
  en: 'English',
} as const;

export type Lang = keyof typeof languages;

export const defaultLang: Lang = 'es';

/** BCP-47 tags for <html lang> and Intl formatting. */
export const localeTags: Record<Lang, string> = {
  es: 'es-CO',
  en: 'en-US',
};

const es = {
  /* ---------------------------------------------------------------- meta */
  'meta.title': 'RestroLogic — El sistema operativo de tu restaurante',
  'meta.description':
    'Software todo-en-uno para restaurantes: pedidos en mesa, cocina en tiempo real, inventarios con recetas, caja y cierres, productos y reportes por sede. Todo en una sola plataforma.',

  /* ----------------------------------------------------------------- nav */
  'nav.features': 'Funciones',
  'nav.modules': 'Módulos',
  'nav.how': 'Cómo funciona',
  'nav.pricing': 'Precios',
  'nav.faq': 'Preguntas',
  'nav.contact': 'Contacto',
  'nav.menu': 'Menú',
  'nav.theme': 'Cambiar tema',
  'nav.language': 'Idioma',
  'nav.skip': 'Ir al contenido principal',

  /* ---------------------------------------------------------------- hero */
  'hero.badge': 'Diseñado para restaurantes de verdad',
  'hero.title.1': 'El sistema operativo',
  'hero.title.2': 'de tu restaurante',
  'hero.lede':
    'Desde que el mesero toma la orden hasta que cierras la caja. RestroLogic conecta mesas, cocina, inventario y reportes en una sola plataforma — sin papeles, sin cuadernos, sin sorpresas al final del día.',
  'hero.cta.primary': 'Solicitar demo',
  'hero.cta.secondary': 'Ver los módulos',
  'hero.proof.1.num': '40%',
  'hero.proof.1.label': 'Menos tiempo por orden',
  'hero.proof.2.num': '100%',
  'hero.proof.2.label': 'Trazabilidad de caja',
  'hero.proof.3.num': '24/7',
  'hero.proof.3.label': 'En la nube',

  /* ------------------------------------------------- hero: app mock chrome */
  'mock.url': 'app.restrologic.com/dashboard',
  'mock.title': 'Servicio de hoy',
  'mock.subtitle': 'Sede Centro · Turno noche',
  'mock.kpi.1': 'Ventas',
  'mock.kpi.2': 'Órdenes',
  'mock.kpi.3': 'Ticket prom.',
  'mock.floor': 'Salón',
  'mock.tickets': 'En curso',
  'mock.state.kitchen': 'Cocina',
  'mock.state.ready': 'Listo',
  'mock.state.paid': 'Pagado',
  'mock.card.kds.title': 'Mesa 12 · Listo para servir',
  'mock.card.kds.meta': '2 platos · 6 min en cocina',
  'mock.card.stock.title': 'Stock bajo: Lomo de res',
  'mock.card.stock.meta': 'Quedan 2.4 kg · alerta automática',
  'mock.card.cash.title': 'Cierre de caja cuadrado',
  'mock.card.cash.meta': 'Sin diferencias · 21:40',

  /* ------------------------------------------------------------- marquee */
  'marquee.label': 'Todo lo que tu operación necesita',
  'marquee.1': 'Pedidos en mesa',
  'marquee.2': 'Cocina en vivo',
  'marquee.3': 'Inventarios',
  'marquee.4': 'Recetas y costos',
  'marquee.5': 'Cierre de caja',
  'marquee.6': 'Multi-sede',
  'marquee.7': 'Reportes',
  'marquee.8': 'Permisos por rol',

  /* ------------------------------------------------------------ pipeline */
  'pipeline.eyebrow': 'El flujo completo',
  'pipeline.title': 'De la mesa a la caja, sin perder un solo pedido',
  'pipeline.lede':
    'Cada orden viaja por un flujo con estados claros. Todos ven lo mismo, al mismo tiempo.',
  'pipeline.1.title': 'Se toma la orden',
  'pipeline.1.text':
    'El mesero abre la mesa desde su celular o tablet, arma el pedido con modificadores y lo envía. Sin repetir la comanda.',
  'pipeline.1.time': 'Paso 1 · ~30 s',
  'pipeline.2.title': 'Cocina la recibe',
  'pipeline.2.text':
    'La comanda aparece al instante en la pantalla de cocina, ordenada por tiempo. El cocinero marca cada plato al avanzar.',
  'pipeline.2.time': 'Paso 2 · en vivo',
  'pipeline.3.title': 'Listo para servir',
  'pipeline.3.text':
    'El mesero recibe el aviso apenas el plato está listo. Menos vueltas a la cocina, menos platos fríos.',
  'pipeline.3.time': 'Paso 3 · notificación',
  'pipeline.4.title': 'Se cobra y se cierra',
  'pipeline.4.text':
    'Divides la cuenta, registras el medio de pago y al final del turno el cierre de caja se cuadra solo.',
  'pipeline.4.time': 'Paso 4 · cierre automático',

  /* ------------------------------------------------------------ features */
  'features.eyebrow': 'Funciones',
  'features.title': 'Un módulo para cada parte de tu operación',
  'features.lede':
    'No es un POS con extras pegados. Cada área del restaurante tiene su propia herramienta, y todas comparten la misma información.',

  'features.orders.title': 'Pedidos en mesa',
  'features.orders.text':
    'Mapa del salón con el estado de cada mesa en tiempo real. Toma órdenes, agrega productos, divide cuentas y traslada mesas.',
  'features.orders.1': 'Mapa de salón por zonas',
  'features.orders.2': 'Modificadores y notas por plato',
  'features.orders.3': 'División y traslado de cuentas',

  'features.kitchen.title': 'Cocina en tiempo real',
  'features.kitchen.text':
    'Pantalla de cocina con las comandas ordenadas por antigüedad. Cada estación ve solo lo suyo y marca el avance plato por plato.',
  'features.kitchen.1': 'Estados por plato, no por orden',
  'features.kitchen.2': 'Alertas por tiempo de preparación',
  'features.kitchen.3': 'Aviso automático al mesero',

  'features.inventory.title': 'Inventarios y recetas',
  'features.inventory.text':
    'Define la receta de cada plato y el inventario se descuenta solo al vender. Sabes tu costo real y tu margen por producto.',
  'features.inventory.1': 'Descuento automático por receta',
  'features.inventory.2': 'Alertas de stock mínimo',
  'features.inventory.3': 'Costo y margen por plato',

  'features.cash.title': 'Caja y cierres',
  'features.cash.text':
    'Apertura y cierre de caja con arqueo por medio de pago. Cada movimiento queda registrado con usuario, hora y motivo.',
  'features.cash.1': 'Arqueo por medio de pago',
  'features.cash.2': 'Entradas y salidas justificadas',
  'features.cash.3': 'Reporte de cierre por turno',

  'features.products.title': 'Productos y recetas',
  'features.products.text':
    'Tu carta completa con variantes de precio por tamaño, categorías, y la receta de cada plato conectada al inventario.',
  'features.products.1': 'Variantes de precio por tamaño',
  'features.products.2': 'Categorías y subcategorías',
  'features.products.3': 'Receta enlazada a materias primas',

  'features.reports.title': 'Reportes y multi-sede',
  'features.reports.text':
    'Ventas, productos más vendidos, flujo de caja e historial de órdenes. Filtra por rango de fechas, sede o usuario.',
  'features.reports.1': 'Reportes por rango de fechas',
  'features.reports.2': 'Historial completo de órdenes',
  'features.reports.3': 'Consolidado y comparativo entre sedes',

  /* ------------------------------------------------------------- modules */
  'modules.eyebrow': 'Dentro del producto',
  'modules.title': 'Estas son las pantallas reales',
  'modules.lede':
    'Capturas del producto funcionando, no maquetas. Cada módulo está pensado para usarse en medio del servicio.',
  'modules.tag': 'Módulo',

  'modules.admin.title': 'Dashboard administrativo',
  'modules.admin.text':
    'El estado del negocio en una pantalla: ventas del día, estado de caja, mesas ocupadas y la cola de cocina, todo en tiempo real.',
  'modules.admin.1': 'Ventas, caja y mesas en vivo',
  'modules.admin.2': 'Cola de cocina y servicio al instante',
  'modules.admin.3': 'Selector de sede en la barra superior',
  'modules.admin.alt':
    'Dashboard administrativo de RestroLogic con ventas del día, estado de caja, mesas ocupadas y la cola de cocina en tiempo real',

  'modules.pos.title': 'Punto de venta y mesas',
  'modules.pos.text':
    'El monitor del salón con el estado de cada mesa: disponible, ocupada, reservada o bloqueada, con su tiempo y su comanda.',
  'modules.pos.1': 'Estados de mesa en tiempo real',
  'modules.pos.2': 'Tiempo transcurrido y número de comanda',
  'modules.pos.3': 'Órdenes activas con cobro en un clic',
  'modules.pos.alt':
    'Monitor de mesas de RestroLogic mostrando el estado, el tiempo y la comanda de cada mesa del salón',

  'modules.inventory.title': 'Inventario y materias primas',
  'modules.inventory.text':
    'Cada insumo con su costo unitario y sus existencias, ajustables en un clic desde la misma pantalla.',
  'modules.inventory.1': 'Costo unitario y existencias por insumo',
  'modules.inventory.2': 'Ajuste rápido de stock',
  'modules.inventory.3': 'Alta y edición sin salir de la lista',
  'modules.inventory.alt':
    'Módulo de inventario de RestroLogic mostrando materias primas con su costo unitario, existencias y el formulario de edición',

  'modules.reports.title': 'Reportes y auditoría',
  'modules.reports.text':
    'El historial completo de órdenes y movimientos de caja en el rango de fechas que elijas, exportable a Excel.',
  'modules.reports.1': 'Filtro por rango de fechas',
  'modules.reports.2': 'Detalle por orden, mesero y estado',
  'modules.reports.3': 'Exportación a Excel',
  'modules.reports.alt':
    'Reporte de órdenes de RestroLogic con fecha, cliente, mesero, subtotal, propina, total y estado de cada orden',

  /* --------------------------------------------------------------- galería */
  'gallery.eyebrow': 'Más pantallas',
  'gallery.title': 'El resto del producto',
  'gallery.lede':
    'Explora las demás pantallas con las que tu equipo trabaja todos los días.',
  'gallery.products.title': 'Catálogo de productos',
  'gallery.products.text':
    'Platos, bebidas y variantes de precio por tamaño, cada uno con su receta y su categoría.',
  'gallery.products.alt':
    'Catálogo de productos de RestroLogic con platos, categorías y variantes de precio por tamaño',
  'gallery.orders.title': 'Órdenes activas',
  'gallery.orders.text':
    'Seguimiento de cada comanda en curso: qué se prepara, qué está listo y cuánto suma la cuenta.',
  'gallery.orders.alt':
    'Pantalla de órdenes activas de RestroLogic mostrando el estado de cada comanda y el total a cobrar',
  'gallery.cash.title': 'Caja y arqueo diario',
  'gallery.cash.text':
    'Ventas por medio de pago, ajustes, propinas y el efectivo esperado antes de cerrar el turno.',
  'gallery.cash.alt':
    'Pantalla de caja y arqueo diario de RestroLogic con ventas netas, propinas y efectivo esperado',
  'gallery.cashreport.title': 'Reporte de caja',
  'gallery.cashreport.text':
    'El consolidado del período: cobros en efectivo y digitales, propinas y saldo estimado.',
  'gallery.cashreport.alt':
    'Reporte de caja de RestroLogic con el resumen consolidado de cobros, propinas y saldo del período',

  /* ---------------------------------------------------------- próximamente */
  'soon.badge': 'Próximamente',
  'soon.title': 'En camino',
  'soon.lede':
    'Módulos en desarrollo. Los anunciaremos aquí en cuanto estén listos para producción.',
  'soon.delivery.title': 'Domicilios',
  'soon.delivery.text':
    'Pedidos a domicilio, asignación de repartidores y liquidación por turno.',
  'soon.invoicing.title': 'Facturación electrónica',
  'soon.invoicing.text':
    'Emisión con validación DIAN, CUFE y envío automático al cliente.',
  'soon.menu.title': 'Menú público QR',
  'soon.menu.text':
    'Tu carta en línea para que el cliente ordene desde la mesa con su celular.',

  /* --------------------------------------------------------------- stats */
  'stats.1.num': '6',
  'stats.1.label': 'Módulos integrados',
  'stats.2.num': '3',
  'stats.2.label': 'Segundos de mesa a cocina',
  'stats.3.num': '1',
  'stats.3.label': 'Sola fuente de datos',
  'stats.4.num': '0',
  'stats.4.label': 'Instalaciones en equipos',

  /* ----------------------------------------------------------------- how */
  'how.eyebrow': 'Puesta en marcha',
  'how.title': 'Operando en tres pasos',
  'how.lede':
    'Sin servidores, sin instalaciones y sin parar el servicio. Funciona en cualquier navegador.',
  'how.1.title': 'Configuramos tu carta',
  'how.1.text':
    'Cargamos productos, categorías, recetas, mesas e impuestos. Si ya tienes la información en Excel, la migramos por ti.',
  'how.2.title': 'Entrenamos a tu equipo',
  'how.2.text':
    'Una sesión corta por rol: meseros, cocina, caja y administración. La interfaz está pensada para aprenderse en un turno.',
  'how.3.title': 'Abres y mides',
  'how.3.text':
    'Desde el primer servicio tienes reportes reales de ventas, costos y caja para tomar decisiones con datos.',

  /* ------------------------------------------------------------- pricing */
  'pricing.eyebrow': 'Planes',
  'pricing.title': 'Precios claros, sin letra pequeña',
  'pricing.lede':
    'Todos los planes incluyen actualizaciones, respaldos y soporte. Cancela cuando quieras.',
  'pricing.monthly': 'Mensual',
  'pricing.yearly': 'Anual',
  'pricing.save': 'Ahorra 20%',
  'pricing.period.month': '/ mes',
  'pricing.period.year': '/ mes, facturado anual',
  'pricing.popular': 'Más elegido',
  'pricing.note':
    'Precios en USD por sede. ¿Varias sedes o franquicia? Hablemos de un plan a la medida.',

  'pricing.starter.name': 'Esencial',
  'pricing.starter.desc': 'Para restaurantes que arrancan',
  'pricing.starter.cta': 'Empezar',
  'pricing.starter.1': 'Pedidos en mesa y caja',
  'pricing.starter.2': 'Pantalla de cocina',
  'pricing.starter.3': 'Cierre de caja diario',
  'pricing.starter.4': 'Hasta 5 usuarios',

  'pricing.pro.name': 'Profesional',
  'pricing.pro.desc': 'Para operaciones en crecimiento',
  'pricing.pro.cta': 'Solicitar demo',
  'pricing.pro.1': 'Todo lo de Esencial',
  'pricing.pro.2': 'Inventarios con recetas y costos',
  'pricing.pro.3': 'Catálogo con recetas y variantes',
  'pricing.pro.4': 'Reportes por rango de fechas',
  'pricing.pro.5': 'Usuarios ilimitados',

  'pricing.enterprise.name': 'Multi-sede',
  'pricing.enterprise.desc': 'Para cadenas y franquicias',
  'pricing.enterprise.price': 'A medida',
  'pricing.enterprise.cta': 'Hablar con ventas',
  'pricing.enterprise.1': 'Todo lo de Profesional',
  'pricing.enterprise.2': 'Consolidado multi-sede',
  'pricing.enterprise.3': 'Reportes personalizados',
  'pricing.enterprise.4': 'Soporte prioritario',

  /* ----------------------------------------------------------------- faq */
  'faq.eyebrow': 'Preguntas frecuentes',
  'faq.title': 'Lo que suelen preguntarnos',
  'faq.lede':
    '¿Te queda alguna duda? Escríbenos y te respondemos el mismo día.',
  'faq.contact': 'Hacer otra pregunta',

  'faq.1.q': '¿Necesito instalar algo o comprar equipos?',
  'faq.1.a':
    'No. RestroLogic funciona en el navegador, así que sirve en el computador de la caja, en una tablet o en el celular de los meseros. Solo necesitas conexión a internet.',
  'faq.2.q': '¿Qué pasa si se cae el internet en medio del servicio?',
  'faq.2.a':
    'La aplicación mantiene la sesión activa y reintenta la sincronización automáticamente. Cuando la conexión vuelve, las órdenes pendientes se envían sin que pierdas información.',
  'faq.3.q': '¿Puedo controlar qué ve cada empleado?',
  'faq.3.a':
    'Sí. El sistema maneja permisos por rol: puedes definir exactamente qué módulos, reportes y acciones puede usar cada persona, y quién autoriza anulaciones o descuentos.',
  'faq.4.q': '¿El inventario se descuenta solo?',
  'faq.4.a':
    'Sí, siempre que el plato tenga receta. Al vender un producto, el sistema descuenta los insumos según su receta y actualiza el costo, así ves tu margen real por plato.',
  'faq.5.q': '¿Puedo manejar varias sedes?',
  'faq.5.a':
    'Sí. Cada sede opera con su propia caja, inventario y equipo, y desde el panel de administración ves el consolidado y puedes comparar el desempeño entre sedes.',
  'faq.6.q': '¿Cuánto tarda la implementación?',
  'faq.6.a':
    'Depende del tamaño de la carta, pero un restaurante estándar queda operando en pocos días. Nosotros cargamos productos y recetas contigo antes de salir en vivo.',

  /* ----------------------------------------------------------------- cta */
  'cta.eyebrow': 'Demo sin costo',
  'cta.title': 'Veamos cómo funciona con tu carta',
  'cta.text':
    'Agenda una demo de 30 minutos. Te mostramos el flujo completo con productos de tu propio restaurante y resolvemos tus dudas en vivo.',
  'cta.perk.1': 'Demo personalizada, sin compromiso',
  'cta.perk.2': 'Migración de tu carta incluida',
  'cta.perk.3': 'Acompañamiento en la puesta en marcha',

  'form.name': 'Nombre',
  'form.name.placeholder': 'Tu nombre',
  'form.email': 'Correo',
  'form.email.placeholder': 'tu@restaurante.com',
  'form.restaurant': 'Restaurante',
  'form.restaurant.placeholder': 'Nombre del restaurante',
  'form.phone': 'Teléfono',
  'form.phone.placeholder': '+57 300 000 0000',
  'form.message': 'Cuéntanos de tu operación',
  'form.message.placeholder':
    '¿Cuántas mesas y sedes manejas? ¿Qué es lo que más te cuesta hoy?',
  'form.submit': 'Solicitar mi demo',
  'form.privacy': 'Solo usamos tus datos para contactarte. Sin spam, nunca.',

  /* -------------------------------------------------------------- footer */
  'footer.tagline':
    'Software de gestión para restaurantes, bares y cadenas. Construido junto a operadores que viven el servicio todos los días.',
  'footer.col.product': 'Producto',
  'footer.col.company': 'Compañía',
  'footer.col.legal': 'Legal',
  'footer.privacy': 'Política de privacidad',
  'footer.terms': 'Términos del servicio',
  'footer.about': 'Sobre nosotros',
  'footer.rights': 'Todos los derechos reservados.',
  'footer.built': 'Hecho por',
  'footer.social': 'Redes sociales',
} as const;

/** The canonical key set. Every other locale must satisfy this shape. */
export type TranslationKey = keyof typeof es;
type Dictionary = Record<TranslationKey, string>;

const en: Dictionary = {
  /* ---------------------------------------------------------------- meta */
  'meta.title': 'RestroLogic — The operating system for your restaurant',
  'meta.description':
    'All-in-one restaurant software: table ordering, live kitchen display, recipe-based inventory, cash control and closing, products and per-location reports. One platform for the whole operation.',

  /* ----------------------------------------------------------------- nav */
  'nav.features': 'Features',
  'nav.modules': 'Modules',
  'nav.how': 'How it works',
  'nav.pricing': 'Pricing',
  'nav.faq': 'FAQ',
  'nav.contact': 'Contact',
  'nav.menu': 'Menu',
  'nav.theme': 'Toggle theme',
  'nav.language': 'Language',
  'nav.skip': 'Skip to main content',

  /* ---------------------------------------------------------------- hero */
  'hero.badge': 'Built for real restaurants',
  'hero.title.1': 'The operating system',
  'hero.title.2': 'for your restaurant',
  'hero.lede':
    'From the moment a server takes the order to the moment you close the register. RestroLogic connects tables, kitchen, inventory and reporting in one platform — no paper tickets, no notebooks, no surprises at the end of the night.',
  'hero.cta.primary': 'Book a demo',
  'hero.cta.secondary': 'See the modules',
  'hero.proof.1.num': '40%',
  'hero.proof.1.label': 'Less time per order',
  'hero.proof.2.num': '100%',
  'hero.proof.2.label': 'Cash traceability',
  'hero.proof.3.num': '24/7',
  'hero.proof.3.label': 'Cloud based',

  /* ------------------------------------------------- hero: app mock chrome */
  'mock.url': 'app.restrologic.com/dashboard',
  'mock.title': "Today's service",
  'mock.subtitle': 'Downtown · Evening shift',
  'mock.kpi.1': 'Sales',
  'mock.kpi.2': 'Orders',
  'mock.kpi.3': 'Avg. ticket',
  'mock.floor': 'Floor',
  'mock.tickets': 'In progress',
  'mock.state.kitchen': 'Kitchen',
  'mock.state.ready': 'Ready',
  'mock.state.paid': 'Paid',
  'mock.card.kds.title': 'Table 12 · Ready to serve',
  'mock.card.kds.meta': '2 dishes · 6 min in kitchen',
  'mock.card.stock.title': 'Low stock: Beef loin',
  'mock.card.stock.meta': '2.4 kg left · automatic alert',
  'mock.card.cash.title': 'Register closed clean',
  'mock.card.cash.meta': 'No discrepancies · 9:40 pm',

  /* ------------------------------------------------------------- marquee */
  'marquee.label': 'Everything your operation needs',
  'marquee.1': 'Table ordering',
  'marquee.2': 'Live kitchen',
  'marquee.3': 'Inventory',
  'marquee.4': 'Recipes & costs',
  'marquee.5': 'Cash closing',
  'marquee.6': 'Multi-location',
  'marquee.7': 'Reports',
  'marquee.8': 'Role permissions',

  /* ------------------------------------------------------------ pipeline */
  'pipeline.eyebrow': 'The full flow',
  'pipeline.title': 'From the table to the register, without losing a single order',
  'pipeline.lede':
    'Every order moves through clear states. Everyone sees the same thing, at the same time.',
  'pipeline.1.title': 'The order is taken',
  'pipeline.1.text':
    'The server opens the table from a phone or tablet, builds the order with modifiers and sends it. No writing the ticket twice.',
  'pipeline.1.time': 'Step 1 · ~30 s',
  'pipeline.2.title': 'The kitchen receives it',
  'pipeline.2.text':
    'The ticket appears instantly on the kitchen display, sorted by wait time. Cooks mark each dish as it progresses.',
  'pipeline.2.time': 'Step 2 · live',
  'pipeline.3.title': 'Ready to serve',
  'pipeline.3.text':
    'The server is notified the moment a dish is up. Fewer trips to the pass, fewer cold plates.',
  'pipeline.3.time': 'Step 3 · notification',
  'pipeline.4.title': 'Paid and closed',
  'pipeline.4.text':
    'Split the check, record the payment method, and at the end of the shift the register reconciles itself.',
  'pipeline.4.time': 'Step 4 · auto closing',

  /* ------------------------------------------------------------ features */
  'features.eyebrow': 'Features',
  'features.title': 'A module for every part of your operation',
  'features.lede':
    "It isn't a POS with add-ons bolted on. Every area of the restaurant gets its own tool, and they all share the same data.",

  'features.orders.title': 'Table ordering',
  'features.orders.text':
    'A live floor map with the status of every table. Take orders, add items, split checks and move parties between tables.',
  'features.orders.1': 'Floor map by zone',
  'features.orders.2': 'Modifiers and notes per dish',
  'features.orders.3': 'Split and transfer checks',

  'features.kitchen.title': 'Live kitchen display',
  'features.kitchen.text':
    'A kitchen screen with tickets sorted by age. Each station sees only its own items and marks progress dish by dish.',
  'features.kitchen.1': 'Status per dish, not per order',
  'features.kitchen.2': 'Prep-time alerts',
  'features.kitchen.3': 'Automatic server notification',

  'features.inventory.title': 'Inventory & recipes',
  'features.inventory.text':
    'Define a recipe for each dish and inventory depletes itself on every sale. You always know your real cost and margin per item.',
  'features.inventory.1': 'Automatic recipe-based depletion',
  'features.inventory.2': 'Minimum-stock alerts',
  'features.inventory.3': 'Cost and margin per dish',

  'features.cash.title': 'Cash control & closing',
  'features.cash.text':
    'Open and close the register with a count by payment method. Every movement is logged with user, time and reason.',
  'features.cash.1': 'Count by payment method',
  'features.cash.2': 'Justified cash in and out',
  'features.cash.3': 'Closing report per shift',

  'features.products.title': 'Products & recipes',
  'features.products.text':
    'Your full menu with per-size price variants, categories, and each dish’s recipe wired straight into inventory.',
  'features.products.1': 'Per-size price variants',
  'features.products.2': 'Categories and subcategories',
  'features.products.3': 'Recipe linked to raw materials',

  'features.reports.title': 'Reports & multi-location',
  'features.reports.text':
    'Sales, best sellers, cash flow and full order history. Filter by date range, location or user.',
  'features.reports.1': 'Reports by date range',
  'features.reports.2': 'Complete order history',
  'features.reports.3': 'Consolidated cross-location comparison',

  /* ------------------------------------------------------------- modules */
  'modules.eyebrow': 'Inside the product',
  'modules.title': 'These are the actual screens',
  'modules.lede':
    'Captures of the product running, not mockups. Every module is designed to be used in the middle of service.',
  'modules.tag': 'Module',

  'modules.admin.title': 'Admin dashboard',
  'modules.admin.text':
    'The state of the business on one screen: today’s sales, register status, occupied tables and the kitchen queue, all live.',
  'modules.admin.1': 'Live sales, cash and tables',
  'modules.admin.2': 'Kitchen and service queue at a glance',
  'modules.admin.3': 'Location switcher in the top bar',
  'modules.admin.alt':
    'RestroLogic admin dashboard showing today’s sales, register status, occupied tables and the live kitchen queue',

  'modules.pos.title': 'Point of sale & tables',
  'modules.pos.text':
    'The floor monitor with every table’s status — free, occupied, reserved or blocked — plus elapsed time and its open ticket.',
  'modules.pos.1': 'Live table states',
  'modules.pos.2': 'Elapsed time and ticket number',
  'modules.pos.3': 'Active orders, one-click payment',
  'modules.pos.alt':
    'RestroLogic table monitor showing the status, elapsed time and ticket for every table on the floor',

  'modules.inventory.title': 'Inventory & raw materials',
  'modules.inventory.text':
    'Every ingredient with its unit cost and stock on hand, adjustable in one click from the same screen.',
  'modules.inventory.1': 'Unit cost and stock per ingredient',
  'modules.inventory.2': 'Quick stock adjustment',
  'modules.inventory.3': 'Create and edit without leaving the list',
  'modules.inventory.alt':
    'RestroLogic inventory module showing raw materials with unit cost, stock on hand and the edit form',

  'modules.reports.title': 'Reports & audit',
  'modules.reports.text':
    'The full history of orders and cash movements over any date range you choose, exportable to Excel.',
  'modules.reports.1': 'Filter by date range',
  'modules.reports.2': 'Detail per order, server and status',
  'modules.reports.3': 'Export to Excel',
  'modules.reports.alt':
    'RestroLogic order report showing date, customer, server, subtotal, tip, total and status for each order',

  /* --------------------------------------------------------------- gallery */
  'gallery.eyebrow': 'More screens',
  'gallery.title': 'The rest of the product',
  'gallery.lede':
    'Browse the other screens your team works with every day.',
  'gallery.products.title': 'Product catalogue',
  'gallery.products.text':
    'Dishes, drinks and per-size price variants, each with its own recipe and category.',
  'gallery.products.alt':
    'RestroLogic product catalogue showing dishes, categories and per-size price variants',
  'gallery.orders.title': 'Active orders',
  'gallery.orders.text':
    'Track every open ticket: what is being prepared, what is ready, and what the check adds up to.',
  'gallery.orders.alt':
    'RestroLogic active orders screen showing the status of each ticket and the total to charge',
  'gallery.cash.title': 'Cash & daily count',
  'gallery.cash.text':
    'Sales by payment method, adjustments, tips and expected cash before closing the shift.',
  'gallery.cash.alt':
    'RestroLogic cash and daily count screen showing net sales, tips and expected cash',
  'gallery.cashreport.title': 'Cash report',
  'gallery.cashreport.text':
    'The consolidated period view: cash and digital takings, tips and estimated balance.',
  'gallery.cashreport.alt':
    'RestroLogic cash report showing the consolidated summary of takings, tips and period balance',

  /* ----------------------------------------------------------- coming soon */
  'soon.badge': 'Coming soon',
  'soon.title': 'On the way',
  'soon.lede':
    'Modules in development. We will announce them here the moment they are production-ready.',
  'soon.delivery.title': 'Deliveries',
  'soon.delivery.text':
    'Delivery orders, driver assignment and per-shift settlement.',
  'soon.invoicing.title': 'Electronic invoicing',
  'soon.invoicing.text':
    'Issuing with tax-authority validation, CUFE and automatic delivery to the customer.',
  'soon.menu.title': 'Public QR menu',
  'soon.menu.text':
    'Your menu online so guests can order from the table on their own phone.',

  /* --------------------------------------------------------------- stats */
  'stats.1.num': '6',
  'stats.1.label': 'Integrated modules',
  'stats.2.num': '3',
  'stats.2.label': 'Seconds from table to kitchen',
  'stats.3.num': '1',
  'stats.3.label': 'Single source of truth',
  'stats.4.num': '0',
  'stats.4.label': 'Installs on your machines',

  /* ----------------------------------------------------------------- how */
  'how.eyebrow': 'Getting started',
  'how.title': 'Up and running in three steps',
  'how.lede':
    'No servers, no installs and no pause in service. It runs in any browser.',
  'how.1.title': 'We set up your menu',
  'how.1.text':
    'We load products, categories, recipes, tables and taxes. If your data is already in a spreadsheet, we migrate it for you.',
  'how.2.title': 'We train your team',
  'how.2.text':
    'One short session per role: servers, kitchen, cashier and management. The interface is designed to be learned in a single shift.',
  'how.3.title': 'You open and measure',
  'how.3.text':
    'From the very first service you get real reports on sales, costs and cash so you can decide with data.',

  /* ------------------------------------------------------------- pricing */
  'pricing.eyebrow': 'Plans',
  'pricing.title': 'Clear pricing, no fine print',
  'pricing.lede':
    'Every plan includes updates, backups and support. Cancel whenever you want.',
  'pricing.monthly': 'Monthly',
  'pricing.yearly': 'Annual',
  'pricing.save': 'Save 20%',
  'pricing.period.month': '/ month',
  'pricing.period.year': '/ month, billed annually',
  'pricing.popular': 'Most chosen',
  'pricing.note':
    'Prices in USD per location. Multiple locations or a franchise? Let’s talk about a tailored plan.',

  'pricing.starter.name': 'Essential',
  'pricing.starter.desc': 'For restaurants getting started',
  'pricing.starter.cta': 'Get started',
  'pricing.starter.1': 'Table ordering and register',
  'pricing.starter.2': 'Kitchen display',
  'pricing.starter.3': 'Daily cash closing',
  'pricing.starter.4': 'Up to 5 users',

  'pricing.pro.name': 'Professional',
  'pricing.pro.desc': 'For growing operations',
  'pricing.pro.cta': 'Book a demo',
  'pricing.pro.1': 'Everything in Essential',
  'pricing.pro.2': 'Inventory with recipes and costs',
  'pricing.pro.3': 'Catalogue with recipes and variants',
  'pricing.pro.4': 'Reports by date range',
  'pricing.pro.5': 'Unlimited users',

  'pricing.enterprise.name': 'Multi-location',
  'pricing.enterprise.desc': 'For chains and franchises',
  'pricing.enterprise.price': 'Custom',
  'pricing.enterprise.cta': 'Talk to sales',
  'pricing.enterprise.1': 'Everything in Professional',
  'pricing.enterprise.2': 'Consolidated multi-location view',
  'pricing.enterprise.3': 'Custom reports',
  'pricing.enterprise.4': 'Priority support',

  /* ----------------------------------------------------------------- faq */
  'faq.eyebrow': 'FAQ',
  'faq.title': 'What people usually ask us',
  'faq.lede': 'Still have a question? Write to us and we answer the same day.',
  'faq.contact': 'Ask something else',

  'faq.1.q': 'Do I need to install anything or buy hardware?',
  'faq.1.a':
    'No. RestroLogic runs in the browser, so it works on the cashier computer, a tablet or your servers’ phones. All you need is an internet connection.',
  'faq.2.q': 'What happens if the internet drops mid-service?',
  'faq.2.a':
    'The app keeps the session alive and retries synchronisation automatically. When the connection returns, pending orders are sent without losing information.',
  'faq.3.q': 'Can I control what each employee sees?',
  'faq.3.a':
    'Yes. The system handles role-based permissions: you define exactly which modules, reports and actions each person can use, and who authorises voids or discounts.',
  'faq.4.q': 'Does inventory deplete automatically?',
  'faq.4.a':
    'Yes, whenever a dish has a recipe. When you sell an item, the system deducts its ingredients according to the recipe and updates the cost, so you see your real margin per dish.',
  'faq.5.q': 'Can I manage multiple locations?',
  'faq.5.a':
    'Yes. Each location runs its own register, inventory and staff, and from the admin dashboard you see the consolidated view and can compare performance across locations.',
  'faq.6.q': 'How long does implementation take?',
  'faq.6.a':
    'It depends on the size of your menu, but a standard restaurant is live within a few days. We load products and recipes with you before you go live.',

  /* ----------------------------------------------------------------- cta */
  'cta.eyebrow': 'Free demo',
  'cta.title': 'Let’s see how it works with your own menu',
  'cta.text':
    'Book a 30-minute demo. We walk through the full flow using products from your own restaurant and answer your questions live.',
  'cta.perk.1': 'Personalised demo, no commitment',
  'cta.perk.2': 'Menu migration included',
  'cta.perk.3': 'Hands-on help during rollout',

  'form.name': 'Name',
  'form.name.placeholder': 'Your name',
  'form.email': 'Email',
  'form.email.placeholder': 'you@restaurant.com',
  'form.restaurant': 'Restaurant',
  'form.restaurant.placeholder': 'Restaurant name',
  'form.phone': 'Phone',
  'form.phone.placeholder': '+1 555 000 0000',
  'form.message': 'Tell us about your operation',
  'form.message.placeholder':
    'How many tables and locations do you run? What is hardest for you today?',
  'form.submit': 'Request my demo',
  'form.privacy': 'We only use your details to contact you. No spam, ever.',

  /* -------------------------------------------------------------- footer */
  'footer.tagline':
    'Management software for restaurants, bars and chains. Built alongside operators who live the service every single day.',
  'footer.col.product': 'Product',
  'footer.col.company': 'Company',
  'footer.col.legal': 'Legal',
  'footer.privacy': 'Privacy policy',
  'footer.terms': 'Terms of service',
  'footer.about': 'About us',
  'footer.rights': 'All rights reserved.',
  'footer.built': 'Built by',
  'footer.social': 'Social media',
};

export const ui: Record<Lang, Dictionary> = { es, en };
