/** @type {import('tailwindcss').Config} */
module.exports = {
    corePlugins: {
        preflight: false,
    },
    content: ['../**/templates/**/*.html', '../**/templates/**/*.jinja'],
    theme: {
        extend: {
            colors: {

            }
        }
    }
}
