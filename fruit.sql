/*
Navicat MySQL Data Transfer

Source Server         : FRUIT
Source Server Version : 50611
Source Host           : localhost:3306
Source Database       : fruit

Target Server Type    : MYSQL
Target Server Version : 50611
File Encoding         : 65001

Date: 2017-05-20 18:42:12
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for fruit_bill_bill
-- ----------------------------
DROP TABLE IF EXISTS `fruit_bill_bill`;
CREATE TABLE `fruit_bill_bill` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime DEFAULT NULL,
  `total_money` float DEFAULT NULL,
  `next_money` float DEFAULT NULL,
  `level_money` float DEFAULT NULL,
  `has_filled` int(11) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_bill_bill
-- ----------------------------
INSERT INTO `fruit_bill_bill` VALUES ('7', '2017-03-01 00:00:00', '0', '1900', '-1900', '0', '3', '1');

-- ----------------------------
-- Table structure for fruit_bill_rebate
-- ----------------------------
DROP TABLE IF EXISTS `fruit_bill_rebate`;
CREATE TABLE `fruit_bill_rebate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime DEFAULT NULL,
  `tickets` varchar(20) DEFAULT NULL,
  `money_price` float DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `bill_id` int(11) DEFAULT NULL,
  `description` text,
  `notice` text,
  PRIMARY KEY (`id`),
  KEY `bill_id` (`bill_id`),
  CONSTRAINT `fruit_bill_rebate_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `fruit_bill_bill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_bill_rebate
-- ----------------------------

-- ----------------------------
-- Table structure for fruit_bill_rebund
-- ----------------------------
DROP TABLE IF EXISTS `fruit_bill_rebund`;
CREATE TABLE `fruit_bill_rebund` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime DEFAULT NULL,
  `tickets` varchar(20) DEFAULT NULL,
  `money_type` enum('现金','支付宝','微信','转账','支票') DEFAULT NULL,
  `money_price` float DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `bill_id` int(11) DEFAULT NULL,
  `notice` text,
  PRIMARY KEY (`id`),
  KEY `bill_id` (`bill_id`),
  CONSTRAINT `fruit_bill_rebund_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `fruit_bill_bill` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_bill_rebund
-- ----------------------------
INSERT INTO `fruit_bill_rebund` VALUES ('1', '2017-03-14 00:00:00', '123', '现金', '1900', '3', '1', '7', '');

-- ----------------------------
-- Table structure for fruit_bill_writeoff
-- ----------------------------
DROP TABLE IF EXISTS `fruit_bill_writeoff`;
CREATE TABLE `fruit_bill_writeoff` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime DEFAULT NULL,
  `tickets` varchar(20) DEFAULT NULL,
  `money_price` float DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `bill_id` int(11) DEFAULT NULL,
  `description` text,
  `notice` text,
  PRIMARY KEY (`id`),
  KEY `bill_id` (`bill_id`),
  CONSTRAINT `fruit_bill_writeoff_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `fruit_bill_bill` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_bill_writeoff
-- ----------------------------

-- ----------------------------
-- Table structure for fruit_departments
-- ----------------------------
DROP TABLE IF EXISTS `fruit_departments`;
CREATE TABLE `fruit_departments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(120) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_departments
-- ----------------------------
INSERT INTO `fruit_departments` VALUES ('1', '管理部', 'admin 管理系统内');
INSERT INTO `fruit_departments` VALUES ('2', '客户', '客户部门');
INSERT INTO `fruit_departments` VALUES ('3', '供应商', '供应商');

-- ----------------------------
-- Table structure for fruit_moneys
-- ----------------------------
DROP TABLE IF EXISTS `fruit_moneys`;
CREATE TABLE `fruit_moneys` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `money_type` enum('现金','支付宝','微信','转账','支票') DEFAULT NULL,
  `tickets` varchar(15) DEFAULT NULL,
  `price` float DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_moneys
-- ----------------------------
INSERT INTO `fruit_moneys` VALUES ('1', '现金', '0000', '0', '1', '2017-02-27 00:00:00');

-- ----------------------------
-- Table structure for fruit_roll_backs
-- ----------------------------
DROP TABLE IF EXISTS `fruit_roll_backs`;
CREATE TABLE `fruit_roll_backs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime DEFAULT NULL,
  `roll_type` varchar(20) DEFAULT NULL,
  `tickets` varchar(15) DEFAULT NULL,
  `sell_id` int(11) DEFAULT NULL,
  `number` smallint(6) DEFAULT NULL,
  `money_id` int(11) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `notice` text,
  `notice_a` text,
  PRIMARY KEY (`id`),
  KEY `sell_id` (`sell_id`),
  CONSTRAINT `fruit_roll_backs_ibfk_1` FOREIGN KEY (`sell_id`) REFERENCES `fruit_sells` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_roll_backs
-- ----------------------------
INSERT INTO `fruit_roll_backs` VALUES ('14', '2017-02-28 00:00:00', '退货', '23', '31', '10', '1', '5', '1', '', '');
INSERT INTO `fruit_roll_backs` VALUES ('15', '2017-02-27 00:00:00', '退货', '123', '31', '10', '1', '5', '1', '', '');
INSERT INTO `fruit_roll_backs` VALUES ('16', '2017-03-13 00:00:00', '退货', '123', '32', '10', '1', '3', '1', '', '');
INSERT INTO `fruit_roll_backs` VALUES ('17', '2017-03-13 00:00:00', '退货', '123', '32', '5', '1', '3', '1', '', '');

-- ----------------------------
-- Table structure for fruit_roll_outs
-- ----------------------------
DROP TABLE IF EXISTS `fruit_roll_outs`;
CREATE TABLE `fruit_roll_outs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime DEFAULT NULL,
  `tickets` varchar(15) DEFAULT NULL,
  `roll_type` enum('报损','转出') DEFAULT NULL,
  `stock_id` int(11) DEFAULT NULL,
  `number` smallint(6) DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `reason` text,
  `notice` text,
  `notice_a` text,
  PRIMARY KEY (`id`),
  KEY `stock_id` (`stock_id`),
  CONSTRAINT `fruit_roll_outs_ibfk_1` FOREIGN KEY (`stock_id`) REFERENCES `fruit_stocks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_roll_outs
-- ----------------------------

-- ----------------------------
-- Table structure for fruit_sells
-- ----------------------------
DROP TABLE IF EXISTS `fruit_sells`;
CREATE TABLE `fruit_sells` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime DEFAULT NULL,
  `stock_id` int(11) DEFAULT NULL,
  `sell_type` enum('销售','代销') DEFAULT NULL,
  `tickets` varchar(15) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `price` float DEFAULT NULL,
  `price_a` float DEFAULT NULL,
  `number` smallint(6) DEFAULT NULL,
  `money_id` int(11) DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `notice` text,
  `notice_a` text,
  PRIMARY KEY (`id`),
  KEY `stock_id` (`stock_id`),
  CONSTRAINT `fruit_sells_ibfk_1` FOREIGN KEY (`stock_id`) REFERENCES `fruit_stocks` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_sells
-- ----------------------------
INSERT INTO `fruit_sells` VALUES ('31', '2017-02-03 00:00:00', '6', '销售', '234', '5', '200', '200', '30', '1', '1', '', '');
INSERT INTO `fruit_sells` VALUES ('32', '2017-03-13 00:00:00', '4', '销售', '123', '3', '120', '120', '20', '1', '1', '', '');

-- ----------------------------
-- Table structure for fruit_stocks
-- ----------------------------
DROP TABLE IF EXISTS `fruit_stocks`;
CREATE TABLE `fruit_stocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime DEFAULT NULL,
  `tickets` varchar(15) DEFAULT NULL,
  `name` varchar(120) DEFAULT NULL,
  `number` smallint(6) DEFAULT NULL,
  `price` float DEFAULT NULL,
  `brand_id` varchar(120) DEFAULT NULL,
  `standard` varchar(120) DEFAULT NULL,
  `car_number` varchar(20) DEFAULT NULL,
  `category` enum('代销','购进') DEFAULT NULL,
  `support_id` int(11) DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `notice` text,
  `notice_a` text,
  `isout` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_stocks
-- ----------------------------
INSERT INTO `fruit_stocks` VALUES ('4', '2017-01-01 00:00:00', '123', '车厘子', '100', '200', '美国', '新进', 'CMS110', '购进', '6', '1', '比较新鲜的', '', '0');
INSERT INTO `fruit_stocks` VALUES ('5', '2017-01-03 00:00:00', '234', '橘子', '200', '0', '智力', '大箱', '', '代销', '4', '1', '', '', '0');
INSERT INTO `fruit_stocks` VALUES ('6', '2017-02-02 00:00:00', '2345', '车厘子', '100', '250', '英国', '大箱', 'CMS110', '购进', '6', '1', '', '', '0');
INSERT INTO `fruit_stocks` VALUES ('7', '2017-02-02 00:00:00', '2354', '橘子', '200', '120', '智力', '进口', 'CJS10001', '代销', '4', '1', '2月份王五代销货', '', '0');

-- ----------------------------
-- Table structure for fruit_users
-- ----------------------------
DROP TABLE IF EXISTS `fruit_users`;
CREATE TABLE `fruit_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(120) DEFAULT NULL,
  `password` varchar(32) DEFAULT NULL,
  `telephone` varchar(11) DEFAULT NULL,
  `department_id` int(11) DEFAULT NULL,
  `state` enum('休眠','活跃') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `department_id` (`department_id`),
  CONSTRAINT `fruit_users_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `fruit_departments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of fruit_users
-- ----------------------------
INSERT INTO `fruit_users` VALUES ('1', 'admin', '21218cca77804d2ba1922c33e0151105', '12345678910', '1', '活跃');
INSERT INTO `fruit_users` VALUES ('2', 'author', '21218cca77804d2ba1922c33e0151105', '12345678910', '1', '活跃');
INSERT INTO `fruit_users` VALUES ('3', '张三', '7215ee9c7d9dc229d2921a40e899ec5f', '', '2', '活跃');
INSERT INTO `fruit_users` VALUES ('4', '王五', '7215ee9c7d9dc229d2921a40e899ec5f', '', '3', '活跃');
INSERT INTO `fruit_users` VALUES ('5', '王五', '7215ee9c7d9dc229d2921a40e899ec5f', '', '2', '活跃');
INSERT INTO `fruit_users` VALUES ('6', '赵四', '7215ee9c7d9dc229d2921a40e899ec5f', '', '3', '活跃');
