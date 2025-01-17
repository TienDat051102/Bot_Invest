import React, { Component } from 'react';
import axios from 'axios';
import { Button, Form, Spinner } from 'react-bootstrap';

class AskQuestion extends Component {
  constructor(props) {
    super(props);
    this.state = {
      question: '',
      response: '',
      loading: false,
      error: '',
    };
  }

  handleQuestionChange = (e) => {
    this.setState({ question: e.target.value, error: '' });
  };

  // Hàm gửi câu hỏi đến API
  handleAsk = async () => {
    const { question } = this.state;
    if (question.trim() === '') {
      this.setState({ error: 'Vui lòng nhập một câu hỏi.' });
      return;
    }

    this.setState({ loading: true, response: '', error: '' });

    try {
      const result = await axios.post('http://localhost:5000/question', {
        question,
      });

      this.setState({ response: result.data.response || 'Không có câu trả lời.' });
    } catch (error) {
      this.setState({ error: 'Đã xảy ra lỗi khi kết nối với API.' });
      console.error(error);
    } finally {
      this.setState({ loading: false });
    }
  };

  render() {
    const { question, response, loading, error } = this.state;

    return (
      <div className="ask-question-container">
        <h1 className="title">Hỏi Trợ Lý Ảo</h1>
        <Form>
          <Form.Group className="mb-3">
            <Form.Control
              type="text"
              placeholder="Đặt một câu hỏi..."
              value={question}
              onChange={this.handleQuestionChange}
              className="question-input"
              disabled={loading}
            />
          </Form.Group>
          <Button
            variant="primary"
            onClick={this.handleAsk}
            disabled={loading}
            className="ask-button"
          >
            {loading ? <Spinner as="span" animation="border" size="sm" /> : 'Hỏi'}
          </Button>
        </Form>
        <div className="response-section">
          {error && <p className="error-text">{error}</p>}
          {response && (
            <p>
              <strong>Trợ Lý Ảo:</strong> {response}
            </p>
          )}
        </div>
      </div>
    );
  }
}

export default AskQuestion;
