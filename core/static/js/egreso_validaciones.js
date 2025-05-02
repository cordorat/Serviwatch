document.addEventListener('DOMContentLoaded', function () {
    // Corregido: Seleccionar los campos correctamente
    const fechaField = document.querySelector('input[name="fecha"]');
    const valorField = document.querySelector('input[name="valor"]');
    const descripcionField = document.querySelector('textarea[name="descripcion"]');
    
    const allFields = [fechaField, valorField, descripcionField];

    function validateField(field) {
        // Remover error anterior
        const errorContainer = field.closest('.mb-3').querySelector('.error-container');
        errorContainer.innerHTML = '';

        const value = field.value.trim();
        let errorMessage = '';

        if (!value) {
            if (field.name === 'fecha') errorMessage = 'La fecha es obligatoria.';
            if (field.name === 'valor') errorMessage = 'El valor es obligatorio.';
            if (field.name === 'descripcion') errorMessage = 'La descripción es obligatoria.';
        }
        
        if (field.name === 'valor' && value && parseInt(value) <= 0) {
            errorMessage = 'El valor debe ser mayor que cero.';
        }

        if (errorMessage) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'text-danger small';
            errorDiv.textContent = errorMessage;
            errorContainer.appendChild(errorDiv);
            field.classList.add('is-invalid');
            return false;
        } else {
            field.classList.remove('is-invalid');
            return true;
        }
    }

    // Validación al salir del input
    allFields.forEach(field => {
        if (!field) return; // Evitar errores si no se encuentra el campo
        
        field.addEventListener('blur', function () {
            validateField(this);
        });

        field.addEventListener('input', function () {
            this.classList.remove('is-invalid');
            const errorContainer = this.closest('.mb-3').querySelector('.error-container');
            errorContainer.innerHTML = '';
        });
    });

    const form = document.querySelector('#egresoForm');
    form.addEventListener('submit', function (e) {
        let isValid = true;
        
        allFields.forEach(field => {
            if (!field) return;
            if (!validateField(field)) {
                isValid = false;
            }
        });

        if (!isValid) e.preventDefault();
    });
});