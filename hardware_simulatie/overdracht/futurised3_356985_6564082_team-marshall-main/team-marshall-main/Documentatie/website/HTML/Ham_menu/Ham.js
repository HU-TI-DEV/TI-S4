document.addEventListener("DOMContentLoaded", () => {
    if (document.querySelector(".menutje") || document.querySelector(".onzichtbaar_menutje")) {
        return;
    }

    const menuHtml = `
        <div class="onzichtbaar_menutje" id="onzichtbaar_menutje">
            <ul>
                <li><a href="main.html">Hoofdpagina</a></li>
                <li><a href="installatieMain.html">Installatie</a></li>
                <li><a href="ProcessenBeheer.html">Processen</a></li>
                <li><a href="Aanbeveling.html">Aanbevelingen</a></li>
            </ul>
        </div>
        <nav>
            <button class="menutje" id="menutje" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="onzichtbaar_menutje">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </nav>
    `;

    document.body.insertAdjacentHTML("afterbegin", menuHtml);

    const menutje = document.getElementById("menutje");
    const onzichtbaarMenutje = document.getElementById("onzichtbaar_menutje");

    if (!menutje || !onzichtbaarMenutje) {
        return;
    }

    const toggleMenu = () => {
        const isOpen = menutje.classList.toggle("actief");
        onzichtbaarMenutje.classList.toggle("actief", isOpen);
        menutje.setAttribute("aria-expanded", isOpen ? "true" : "false");
    };

    menutje.addEventListener("click", toggleMenu);

    onzichtbaarMenutje.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            menutje.classList.remove("actief");
            onzichtbaarMenutje.classList.remove("actief");
            menutje.setAttribute("aria-expanded", "false");
        });
    });
});