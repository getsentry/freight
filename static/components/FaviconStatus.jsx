import PropTypes from 'prop-types';
import React from 'react';

class FaviconStatus extends React.Component {
  static propTypes = {
    status: PropTypes.string.isRequired,
    progress: PropTypes.number.isRequired,
  };

  componentDidMount() {
    this.faviconElement = document.querySelector('link[rel*=icon]');
    this.originalFaviconUrl = this.faviconElement.href;
    this.originalTitle = document.title;

    this.updateFavicon();
    this.updateTitle();
  }

  componentDidUpdate() {
    this.updateFavicon();
    this.updateTitle();
  }

  componentWillUnmount() {
    document.title = this.originalTitle;
    this.faviconElement.href = this.originalFaviconUrl;
  }

  getColor() {
    switch (this.props.status) {
      case 'cancelled':
        return '#f9a66d';
      case 'failed':
        return '#e03e2f';
      case 'finished':
        return '#57be8c';
      case 'pending':
        return '#6c5fc7';
      case 'in_progress':
        return '#dbd3e9';
      default:
        return '#777088';
    }
  }

  updateFavicon() {
    const image = document.createElement('img');

    image.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = 16;
      canvas.height = 16;

      const context = canvas.getContext('2d');
      context.drawImage(image, 0, 0, 16, 16);

      context.beginPath();
      context.arc(12, 12, 4, 0, 2 * Math.PI);
      context.fillStyle = '#36323e';
      context.fill();

      context.beginPath();
      context.arc(12, 12, 3, 0, 2 * Math.PI);
      context.fillStyle = this.getColor();
      context.fill();

      this.faviconElement.href = canvas.toDataURL('image/png');
    };

    image.src = this.originalFaviconUrl;
  }

  updateTitle() {
    if (this.props.status === 'in_progress') {
      document.title = `[${this.props.progress}%] ${this.originalTitle}`;
    } else {
      document.title = this.originalTitle;
    }
  }

  render() {
    return null;
  }
}

export default FaviconStatus;
