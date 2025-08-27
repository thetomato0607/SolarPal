import { Component } from "react";
import PropTypes from "prop-types";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught an error", error, info);
  }

  reset = () => {
    this.setState({ hasError: false, error: null });
    if (typeof this.props.onReset === "function") {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      if (typeof this.props.fallback === "function") {
        const Fallback = this.props.fallback;
        return <Fallback error={this.state.error} resetErrorBoundary={this.reset} />;
      }
      return (
        <div role="alert" style={{ padding: 16 }}>
          <p>Something went wrong.</p>
          <button onClick={this.reset} style={{ marginTop: 8 }}>Retry</button>
        </div>
      );
    }
    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node,
  fallback: PropTypes.func,
  onReset: PropTypes.func,
};

