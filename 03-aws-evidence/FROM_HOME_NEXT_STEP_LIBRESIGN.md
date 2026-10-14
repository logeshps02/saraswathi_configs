# From Home — Next Step: LibreSign

Firm folder tree exists under `saraswathi.admin`. Enable **LibreSign** for in-browser PDF signing.

Use Session Manager. Paste each numbered block as **one line**.

Do **not** paste `config.php`.
Do **not** create extra users.
Do **not** upload client PDFs or certificates in this step.

## 1. Enable LibreSign

```sh
sudo -u www-data php /var/www/nextcloud/occ app:enable libresign && sudo -u www-data php /var/www/nextcloud/occ app:list --enabled | grep -Ei 'libresign'
```

Expected: `libresign` enabled with a version. If the app id is different, paste the error only.

## 2. Confirm occ / HTTPS surface

```sh
sudo -u www-data php /var/www/nextcloud/occ list 2>/dev/null | grep -Ei 'libresign' || echo NO_LIBRESIGN_OCC; curl -sI https://files.t-saraswathi.in/apps/libresign/ | head -n 8
```

Expected: some `libresign:` commands or `NO_LIBRESIGN_OCC`. HTTPS not nginx 404 (401/302/200 OK). Do not paste Set-Cookie values.

## 3. Confirmed enable (2026-08-25)

| Item | Value |
|---|---|
| libresign | 14.1.0 enabled |
| occ | configure:cfssl/check/openssl, crl:*, install, uninstall |
| HTTPS `/apps/libresign/` | 401 without login (present) |

Do not paste `Set-Cookie` from curl.

## 4. Check / install signing tools (SSM)

```sh
sudo -u www-data php /var/www/nextcloud/occ libresign:configure:check
```

Paste the full check output. Do not run `libresign:install` until we see what it asks for.

Result (2026-08-25): java / jsignpdf / pdftk **error**; poppler **info**; imagick **success**; openssl-configure **error**.

## 5. Install OS poppler + LibreSign binaries

Downloads can take several minutes. Wait for `$`.

```sh
sudo DEBIAN_FRONTEND=noninteractive apt install -y poppler-utils && sudo -u www-data php /var/www/nextcloud/occ libresign:install --java && sudo -u www-data php /var/www/nextcloud/occ libresign:install --jsignpdf && sudo -u www-data php /var/www/nextcloud/occ libresign:install --pdftk
```

## 6. Configure LibreSign OpenSSL root (internal CA only)

This is **not** a public website cert. CN only. No password in chat.

```sh
sudo -u www-data php /var/www/nextcloud/occ libresign:configure:openssl --cn='Saraswathi LibreSign CA'
```

If it asks for extra flags, paste `--help` output instead of guessing.

## 7. Re-check

```sh
sudo -u www-data php /var/www/nextcloud/occ libresign:configure:check
```

Expected: java, jsignpdf, pdftk, poppler, openssl-configure no longer **error**. Imagick stays success.

## 8. Confirmed (2026-08-25)

| Item | Value |
|---|---|
| libresign | 14.1.0 enabled |
| java | OpenJDK 21.0.8 LTS (LibreSign bundled JRE) |
| JSignPdf | 2.3.0 |
| PDFtk | 3.3.3 |
| poppler | pdfsig/pdfinfo 24.02.0 |
| imagick | loaded |
| openssl-configure | root certificate setup working |
| configure:check | all **success** |

Do not paste LibreSign private keys or the generated CA files.

## Stop

LibreSign install/configure is complete. Sample PDF signing is later in the browser. Do not upload client PDFs yet.
