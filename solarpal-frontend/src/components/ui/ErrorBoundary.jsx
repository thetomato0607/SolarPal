import { Component, cloneElement } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
    this.reset = this.reset.bind(this);
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught error", error, info);
  }

  reset() {
    this.setState({ error: null });
    this.props.onReset?.();
  }

  render() {
    if (this.state.error) {
      const { fallback } = this.props;
      if (typeof fallback === "function") {
        return fallback({ error: this.state.error, reset: this.reset });
      }
      if (fallback) {
        return cloneElement(fallback, { retry: this.reset });
      }
      return (
        <div style={{ padding: 16 }}>
          <p>Something went wrong.</p>
          <button onClick={this.reset}>Retry</button>
        </div>
      );
    }
    return this.props.children;
  }
}
