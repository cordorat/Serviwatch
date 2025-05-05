document.addEventListener("DOMContentLoaded", function() {
    const btnConfirmar = document.getElementById('btnConfirmar');
    const egresoForm = document.getElementById('egresoForm');
    const modal = new bootstrap.Modal(document.getElementById('confirmationModal'));
    
    btnConfirmar.addEventListener('click', function() {
        // Agregar un campo oculto para indicar la acción "confirmar"
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'confirmar';
        hiddenInput.value = 'true';
        egresoForm.appendChild(hiddenInput);
        
        // Mostrar el modal
        modal.show();    
        // Por seguridad, enviar el formulario después de 3 segundos incluso si la animación falla
        setTimeout(function() {
            egresoForm.submit();
        }, 3000);
    });
});