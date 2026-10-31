document.addEventListener("DOMContentLoaded", function () {
    console.log("Citizen Care website loaded successfully.");

    // Close the mobile navigation after clicking a link.
    const navbar = document.getElementById("mainNavbar");

    if (navbar) {
        const links = navbar.querySelectorAll(".nav-link");

        links.forEach(function (link) {
            link.addEventListener("click", function () {
                if (window.innerWidth < 992) {
                    const collapse =
                        bootstrap.Collapse.getInstance(navbar);

                    if (collapse) {
                        collapse.hide();
                    }
                }
            });
        });
    }
});