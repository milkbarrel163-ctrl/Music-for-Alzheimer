import React, { useEffect } from 'react';
import './NotificationModal.css';

const NotificationModal = ({
  type = 'info', // 'success', 'error', 'warning', 'info'
  title,
  message,
  onClose,
  autoClose = true,
  duration = 5000,
  position = 'top-right' // 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'center'
}) => {
  useEffect(() => {
    if (autoClose && duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [autoClose, duration, onClose]);

  const getIcon = () => {
    switch (type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
      default:
        return 'ℹ️';
    }
  };

  const handleBackdropClick = (e) => {
    if (position === 'center' && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className={`notification-modal-backdrop ${position}`}
      onClick={handleBackdropClick}
      role="alert"
      aria-live="polite"
    >
      <div className={`notification-modal ${type} ${position}`}>
        <div className="notification-icon">
          {getIcon()}
        </div>

        <div className="notification-content">
          {title && <h4 className="notification-title">{title}</h4>}
          {message && <p className="notification-message">{message}</p>}
        </div>

        <button
          className="notification-close"
          onClick={onClose}
          aria-label="Close notification"
        >
          ×
        </button>

        {autoClose && (
          <div
            className="notification-progress"
            style={{ animationDuration: `${duration}ms` }}
          />
        )}
      </div>
    </div>
  );
};

export default NotificationModal;