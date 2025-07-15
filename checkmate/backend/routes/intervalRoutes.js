// 인터벌 계산 API 라우트
const express = require('express');
const IntervalService = require('../services/IntervalService');
const auth = require('../middlewares/auth');
const { body, validationResult } = require('express-validator');
const router = express.Router();

const intervalService = new IntervalService();

// 최적 인터벌 계산
router.post('/calculate', [
  body('targetUrl').isURL().withMessage('유효한 URL을 입력해주세요'),
  body('targetTime').isISO8601().withMessage('유효한 날짜 형식을 입력해주세요')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        errors: errors.array()
      });
    }

    const { targetUrl, targetTime } = req.body;
    const userId = req.user?.id || null; // 인증된 사용자 ID (선택적)
    
    const result = await intervalService.calculateOptimalInterval(targetUrl, targetTime, userId);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// 실시간 인터벌 조정
router.post('/adjust', [
  body('targetUrl').isURL().withMessage('유효한 URL을 입력해주세요'),
  body('currentOffset').isInt({ min: 500, max: 10000 }).withMessage('현재 오프셋은 500-10000ms 사이여야 합니다')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        errors: errors.array()
      });
    }

    const { targetUrl, currentOffset } = req.body;
    const result = await intervalService.adjustIntervalBasedOnRealtimeData(targetUrl, currentOffset);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// 배치 인터벌 계산
router.post('/batch', [
  body('requests').isArray({ min: 1, max: 10 }).withMessage('요청은 1-10개 사이여야 합니다'),
  body('requests.*.targetUrl').isURL().withMessage('모든 URL이 유효해야 합니다'),
  body('requests.*.targetTime').isISO8601().withMessage('모든 날짜가 유효해야 합니다')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        errors: errors.array()
      });
    }

    const { requests } = req.body;
    const results = await intervalService.calculateMultipleIntervals(requests);
    
    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// 접속 결과 로깅
router.post('/log-access', auth.optional, [
  body('siteId').optional().isInt().withMessage('유효한 사이트 ID여야 합니다'),
  body('targetTime').isISO8601().withMessage('유효한 목표 시간이어야 합니다'),
  body('actualAccessTime').isISO8601().withMessage('유효한 실제 접속 시간이어야 합니다'),
  body('success').isBoolean().withMessage('성공 여부는 boolean이어야 합니다'),
  body('rtt').optional().isFloat({ min: 0 }).withMessage('RTT는 0 이상이어야 합니다'),
  body('optimalOffset').isInt({ min: 0 }).withMessage('최적 오프셋은 0 이상이어야 합니다'),
  body('confidenceScore').isFloat({ min: 0, max: 1 }).withMessage('신뢰도는 0-1 사이여야 합니다')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        errors: errors.array()
      });
    }

    const {
      siteId,
      targetTime,
      actualAccessTime,
      rtt,
      success,
      optimalOffset,
      confidenceScore
    } = req.body;
    
    const userId = req.user?.id || null;
    
    await intervalService.logAccessAttempt(
      userId,
      siteId,
      targetTime,
      actualAccessTime,
      rtt,
      success,
      optimalOffset,
      confidenceScore
    );
    
    res.json({
      success: true,
      message: '접속 결과가 기록되었습니다'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;