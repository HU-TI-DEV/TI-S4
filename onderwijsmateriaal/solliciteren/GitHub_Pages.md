# GitHub Pages

Om je CV op GitHub Pages te plaatsen moet je een aantal stappen doorlopen:

1. Maak eerst een nieuwe repository. Als het goed is is al bekend hoe je dit doet, maar kijk anders nog eens terug op {{link naar guide voor het opzetten van een repo}}.
2. Upload je CV naar je repository. Het is aan te raden je CV in de root van je repository te plaatsen, maar niet noodzakelijk.
3. Voeg een bestand toe genaamd `index.html`, en plaats daar de onderstaande code in:
```jinja
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en" style="width:100%; height:100%;">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title><{{HIER_DE_TITEL_VAN_JOUW_PAGE}}></title>
</head>
  <body style="width:100%; height:100%; margin:0;">
    <iframe src="https://docs.google.com/gview?url=https://{{GITHUB_NAAM}}.github.io/{{PAD_NAAR_JE_PDF.pdf}}&embedded=true" style="width:100%; height:100%;" frameborder="0"></iframe>
  </body>
</html>
```
4. Pas de `index.html` aan zodat de paars gemarkeerde onderdelen de voor jouw CV relevante informatie bevatten. De ```{{}}``` zijn daar niet meer nodig.
5. Ga naar de Settings van je repository.
6. Klik in de sidebar door naar Pages.
7. Kies onder Source voor de optie `Deploy from a branch`.
8. Kies onder Branch voor de opties `main` (tenzij je de branch anders hebt genoemd) en `/ (root)` (tenzij je de `index.html` niet in de root hebt geplaatst).
9. Hierna kost het mogelijk een paar minuten voordat je Page wordt geupdatet, maar daarna zou je je CV terug moeten kunnen vinden op `https://GITHUB_NAAM.github.io/REPOSITORY_NAAM`. Gefeliciteerd! 

Het is daarna eventueel nog mogelijk om je GitHub Page naar een custom domeinnaam te laten verwijzen als je deze huurt/bezit, maar daar is nu nog geen verdere informatie over.
