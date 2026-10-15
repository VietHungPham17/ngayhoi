document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const ma_sv = document.getElementById('ma_sv').value;
  const ma_phien = document.getElementById('ma_phien').value;
  const messageBox = document.getElementById('messageBox');

  // Reset message box
  messageBox.style.display = 'none';
  messageBox.className = 'alert';

  try {
    const response = await fetch("http://localhost:8000/api/dang-ky", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ma_sv, ma_phien })
    });

    if (response.status === 201) {
      messageBox.textContent = 'Ghi thành công!';
      messageBox.classList.add('alert-success');
      messageBox.style.display = 'block';
    } else if (response.status === 409) {
      const data = await response.json();
      if (data.detail === 'DA_DANG_KY') {
        messageBox.textContent = 'Mã sinh viên này đã đăng ký!';
        messageBox.classList.add('alert-error');
        messageBox.style.display = 'block';
      }
    } else {
      messageBox.textContent = 'Có lỗi xảy ra, vui lòng thử lại.';
      messageBox.classList.add('alert-error');
      messageBox.style.display = 'block';
    }
  } catch (error) {
    messageBox.textContent = 'Không thể kết nối đến máy chủ!';
    messageBox.classList.add('alert-error');
    messageBox.style.display = 'block';
  }
});
