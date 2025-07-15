// 시간 관련 API 라우트
const express = require('express');
const TimeService = require('../services/TimeService');
const router = express.Router();

const timeService = new TimeService();

// 현재 정확한 시간 조회
router.get('/current', async (req, res) => {
  try {
    const currentTime = await timeService.getCurrentTime();
    res.json({
      success: true,
      data: currentTime
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// NTP 동기화 실행
router.post('/sync', async (req, res) => {
  try {
    const syncResult = await timeService.syncWithNTP();
    res.json({
      success: true,
      data: syncResult
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// 동기화 상태 확인
router.get('/sync-status', async (req, res) => {
  try {
    const status = timeService.getSyncStatus();
    res.json({
      success: true,
      data: status
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// 특정 시간대의 현재 시간
router.get('/timezone/:timezone', async (req, res) => {
  try {
    const { timezone } = req.params;
    const timeInTimezone = timeService.getCurrentTimeInTimezone(timezone);
    res.json({
      success: true,
      data: timeInTimezone
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
