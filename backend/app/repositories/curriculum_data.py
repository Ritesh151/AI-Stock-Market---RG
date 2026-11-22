"""
Curriculum Data Seed for RG AI Learn Trading Education Platform.
Provides rich, verified, structured lessons, courses, and deterministic quizzes
covering Beginner, Intermediate, and Advanced Indian Stock Market concepts.
"""

from typing import Any, Dict, List
from app.schemas.learning import (
    CourseDetail,
    DifficultyLevel,
    LearningCategory,
    LessonDetail,
    LessonExample,
    LessonSummary,
    QuestionType,
    QuizOption,
    QuizQuestionInternal,
)

# =====================================================================
# COURSES DATA
# =====================================================================

COURSES_DATA: List[CourseDetail] = [
    # 1. Beginner - Stock Market Basics
    CourseDetail(
        id="course-market-basics",
        title="Indian Stock Market Fundamentals",
        description="Comprehensive beginner orientation to Indian financial exchanges (NSE & BSE), depository participants (CDSL/NSDL), trading accounts, equity types, order execution mechanics, and market terminology.",
        difficulty=DifficultyLevel.BEGINNER,
        category=LearningCategory.STOCK_MARKET_BASICS,
        estimated_duration="60 mins",
        lesson_count=4,
        learning_objectives=[
            "Understand the operational structure of National Stock Exchange (NSE) and Bombay Stock Exchange (BSE).",
            "Differentiate between Demat accounts, Trading accounts, and Bank settlement flows.",
            "Master market orders, limit orders, stop-loss orders, and iceberg executions.",
            "Decode essential market terminology including Bid, Ask, Spread, Circuit Filters, and T+1 settlement cycles.",
        ],
        prerequisites=[],
        lessons=[
            LessonSummary(
                id="lesson-nse-bse-structure",
                course_id="course-market-basics",
                title="NSE, BSE, and Market Ecosystem",
                order=1,
                duration="15 mins",
                category=LearningCategory.STOCK_MARKET_BASICS,
                difficulty=DifficultyLevel.BEGINNER,
            ),
            LessonSummary(
                id="lesson-demat-trading-accounts",
                course_id="course-market-basics",
                title="Demat, Trading Accounts & Clearing Mechanics",
                order=2,
                duration="15 mins",
                category=LearningCategory.STOCK_MARKET_BASICS,
                difficulty=DifficultyLevel.BEGINNER,
            ),
            LessonSummary(
                id="lesson-order-types",
                course_id="course-market-basics",
                title="Market, Limit, and Stop-Loss Orders",
                order=3,
                duration="15 mins",
                category=LearningCategory.STOCK_MARKET_BASICS,
                difficulty=DifficultyLevel.BEGINNER,
            ),
            LessonSummary(
                id="lesson-market-terminology",
                course_id="course-market-basics",
                title="Essential Market Terminology & Circuit Breakers",
                order=4,
                duration="15 mins",
                category=LearningCategory.STOCK_MARKET_BASICS,
                difficulty=DifficultyLevel.BEGINNER,
            ),
        ],
    ),

    # 2. Intermediate - Candlestick Patterns (13 patterns)
    CourseDetail(
        id="course-candlestick-mastery",
        title="Mastering Candlestick Patterns & Price Action",
        description="Deep structural study of Japanese candlestick anatomy and 13 essential single, double, and triple candlestick formations across Indian equity charts.",
        difficulty=DifficultyLevel.INTERMEDIATE,
        category=LearningCategory.CANDLESTICK_PATTERNS,
        estimated_duration="90 mins",
        lesson_count=5,
        learning_objectives=[
            "Analyze candlestick anatomy: real body, upper shadow, lower shadow, and range.",
            "Identify single-candle reversal signals: Doji, Hammer, Inverted Hammer, Shooting Star, and Hanging Man.",
            "Master dual-candle reversal setups: Bullish Engulfing, Bearish Engulfing, Piercing Pattern, and Dark Cloud Cover.",
            "Evaluate multi-candle confirmation patterns: Morning Star, Evening Star, Three White Soldiers, and Three Black Crows.",
            "Understand why candlestick patterns require volume confirmation and structural context before execution.",
        ],
        prerequisites=["course-market-basics"],
        lessons=[
            LessonSummary(
                id="lesson-candle-anatomy-doji",
                course_id="course-candlestick-mastery",
                title="Candlestick Anatomy & The Doji Family",
                order=1,
                duration="15 mins",
                category=LearningCategory.CANDLESTICK_PATTERNS,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-hammer-shooting-star",
                course_id="course-candlestick-mastery",
                title="Hammer, Inverted Hammer, Shooting Star & Hanging Man",
                order=2,
                duration="20 mins",
                category=LearningCategory.CANDLESTICK_PATTERNS,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-engulfing-patterns",
                course_id="course-candlestick-mastery",
                title="Bullish & Bearish Engulfing Formations",
                order=3,
                duration="20 mins",
                category=LearningCategory.CANDLESTICK_PATTERNS,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-piercing-dark-cloud",
                course_id="course-candlestick-mastery",
                title="Piercing Pattern & Dark Cloud Cover",
                order=4,
                duration="15 mins",
                category=LearningCategory.CANDLESTICK_PATTERNS,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-stars-soldiers-crows",
                course_id="course-candlestick-mastery",
                title="Morning Star, Evening Star, Three Soldiers & Crows",
                order=5,
                duration="20 mins",
                category=LearningCategory.CANDLESTICK_PATTERNS,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
        ],
    ),

    # 3. Intermediate - Technical Analysis & Support/Resistance
    CourseDetail(
        id="course-support-resistance",
        title="Support, Resistance & Market Structure",
        description="Learn to identify institutional demand and supply zones, dynamic trendlines, role reversals, breakouts, and false breakout traps.",
        difficulty=DifficultyLevel.INTERMEDIATE,
        category=LearningCategory.SUPPORT_AND_RESISTANCE,
        estimated_duration="50 mins",
        lesson_count=3,
        learning_objectives=[
            "Identify key horizontal support and resistance zones using pivot points and swing highs/lows.",
            "Construct dynamic ascending and descending trendlines with proper anchor points.",
            "Understand the principle of role reversal (broken support turning into resistance and vice versa).",
            "Distinguish legitimate breakout volume expansions from low-liquidity false breakouts.",
        ],
        prerequisites=["course-candlestick-mastery"],
        lessons=[
            LessonSummary(
                id="lesson-horizontal-levels",
                course_id="course-support-resistance",
                title="Horizontal Demand & Supply Zones",
                order=1,
                duration="15 mins",
                category=LearningCategory.SUPPORT_AND_RESISTANCE,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-dynamic-trendlines",
                course_id="course-support-resistance",
                title="Dynamic Trendlines & Channels",
                order=2,
                duration="15 mins",
                category=LearningCategory.SUPPORT_AND_RESISTANCE,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-role-reversal-breakouts",
                course_id="course-support-resistance",
                title="Role Reversal, Breakouts & Fakeouts",
                order=3,
                duration="20 mins",
                category=LearningCategory.SUPPORT_AND_RESISTANCE,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
        ],
    ),

    # 4. Intermediate - Technical Indicators (RSI, MACD, MA, Volume)
    CourseDetail(
        id="course-technical-indicators",
        title="Technical Indicators: RSI, MACD, Moving Averages & Volume",
        description="Master core momentum, trend-following, and volume indicators. Learn calculation concepts, overbought/oversold boundaries, divergences, and common analytical pitfalls.",
        difficulty=DifficultyLevel.INTERMEDIATE,
        category=LearningCategory.TECHNICAL_ANALYSIS,
        estimated_duration="75 mins",
        lesson_count=4,
        learning_objectives=[
            "Calculate and interpret the Relative Strength Index (RSI 14) and identify regular/hidden divergences.",
            "Decode MACD lines, signal lines, histograms, and zero-line crossovers.",
            "Deploy Simple and Exponential Moving Averages (20, 50, 200 EMA) and identify Golden/Death Crosses.",
            "Apply volume spread analysis (VSA) to confirm institutional accumulation or distribution.",
        ],
        prerequisites=["course-support-resistance"],
        lessons=[
            LessonSummary(
                id="lesson-rsi-indicator",
                course_id="course-technical-indicators",
                title="RSI: Momentum, Extremes & Divergences",
                order=1,
                duration="20 mins",
                category=LearningCategory.RSI_INDICATOR,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-macd-indicator",
                course_id="course-technical-indicators",
                title="MACD: Line Crossovers, Histogram & Momentum",
                order=2,
                duration="20 mins",
                category=LearningCategory.MACD_INDICATOR,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-moving-averages",
                course_id="course-technical-indicators",
                title="Moving Averages: SMA, EMA & Golden/Death Crosses",
                order=3,
                duration="15 mins",
                category=LearningCategory.MOVING_AVERAGES,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-volume-analysis",
                course_id="course-technical-indicators",
                title="Volume Analysis: Confirmation, Spikes & Relative Volume",
                order=4,
                duration="20 mins",
                category=LearningCategory.VOLUME_ANALYSIS,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
        ],
    ),

    # 5. Advanced - Risk Management & Position Sizing
    CourseDetail(
        id="course-risk-management",
        title="Institutional Risk Management & Position Sizing",
        description="Mathematical capital preservation frameworks for Indian equities: the 1% risk rule, stop-loss calculations, risk-to-reward profiling, and maximum portfolio drawdown limits.",
        difficulty=DifficultyLevel.ADVANCED,
        category=LearningCategory.RISK_MANAGEMENT,
        estimated_duration="60 mins",
        lesson_count=3,
        learning_objectives=[
            "Formulate dynamic position sizing using account equity and distance to technical invalidation.",
            "Calculate strict Risk-to-Reward (R:R) ratios and understand win-rate vs. expectancy.",
            "Implement maximum daily, weekly, and total drawdown circuit breakers to prevent account blowups.",
        ],
        prerequisites=["course-technical-indicators"],
        lessons=[
            LessonSummary(
                id="lesson-one-percent-rule",
                course_id="course-risk-management",
                title="The 1% Rule & Capital Preservation Formula",
                order=1,
                duration="20 mins",
                category=LearningCategory.RISK_MANAGEMENT,
                difficulty=DifficultyLevel.ADVANCED,
            ),
            LessonSummary(
                id="lesson-position-sizing-inr",
                course_id="course-risk-management",
                title="Exact Position Sizing & Stop-Loss Placement (INR)",
                order=2,
                duration="20 mins",
                category=LearningCategory.RISK_MANAGEMENT,
                difficulty=DifficultyLevel.ADVANCED,
            ),
            LessonSummary(
                id="lesson-risk-reward-expectancy",
                course_id="course-risk-management",
                title="Risk-to-Reward Ratio & Mathematical Expectancy",
                order=3,
                duration="20 mins",
                category=LearningCategory.RISK_MANAGEMENT,
                difficulty=DifficultyLevel.ADVANCED,
            ),
        ],
    ),

    # 6. Advanced - Trading Psychology & Multi-Timeframe Strategy
    CourseDetail(
        id="course-psychology-strategy",
        title="Trading Psychology, Swing Trading & Market Structure",
        description="Master emotional discipline, FOMO control, cognitive biases, multiple timeframe confluence (Monthly/Weekly/Daily/15m), and disciplined swing trading execution.",
        difficulty=DifficultyLevel.ADVANCED,
        category=LearningCategory.TRADING_PSYCHOLOGY,
        estimated_duration="60 mins",
        lesson_count=3,
        learning_objectives=[
            "Identify cognitive biases: confirmation bias, loss aversion, recency bias, and revenge trading.",
            "Execute top-down multiple timeframe analysis (MTFA) from macro trends down to trigger entries.",
            "Structure systematic swing trading campaigns with clear catalysts, targets, and trail stops.",
        ],
        prerequisites=["course-risk-management"],
        lessons=[
            LessonSummary(
                id="lesson-trading-psychology",
                course_id="course-psychology-strategy",
                title="Mastering Trading Psychology & Emotional Discipline",
                order=1,
                duration="20 mins",
                category=LearningCategory.TRADING_PSYCHOLOGY,
                difficulty=DifficultyLevel.ADVANCED,
            ),
            LessonSummary(
                id="lesson-multi-timeframe-analysis",
                course_id="course-psychology-strategy",
                title="Multiple Timeframe Analysis & Market Confluence",
                order=2,
                duration="20 mins",
                category=LearningCategory.SWING_TRADING,
                difficulty=DifficultyLevel.ADVANCED,
            ),
            LessonSummary(
                id="lesson-portfolio-investing",
                course_id="course-psychology-strategy",
                title="Long-Term Investing & Portfolio Diversification",
                order=3,
                duration="20 mins",
                category=LearningCategory.LONG_TERM_INVESTING,
                difficulty=DifficultyLevel.ADVANCED,
            ),
        ],
    ),

    # 7. Intermediate - Fundamental Analysis & Valuation
    CourseDetail(
        id="course-fundamental-analysis",
        title="Fundamental Analysis & Equity Valuation",
        description="Core financial statement interpretation (Balance Sheet, P&L, Cash Flow), key ratios (P/E, P/B, ROE, Debt/Equity), and qualitative moat analysis for Indian enterprises.",
        difficulty=DifficultyLevel.INTERMEDIATE,
        category=LearningCategory.FUNDAMENTAL_ANALYSIS,
        estimated_duration="45 mins",
        lesson_count=2,
        learning_objectives=[
            "Read financial statements: Revenue, EBITDA, PAT, Free Cash Flow, and Working Capital.",
            "Evaluate valuation metrics: Price to Earnings (P/E), Return on Equity (ROE), and Debt-to-Equity.",
        ],
        prerequisites=["course-market-basics"],
        lessons=[
            LessonSummary(
                id="lesson-financial-statements",
                course_id="course-fundamental-analysis",
                title="Reading Financial Statements & Cash Flows",
                order=1,
                duration="20 mins",
                category=LearningCategory.FUNDAMENTAL_ANALYSIS,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
            LessonSummary(
                id="lesson-valuation-metrics",
                course_id="course-fundamental-analysis",
                title="Core Valuation Ratios: P/E, P/B, ROE & ROCE",
                order=2,
                duration="25 mins",
                category=LearningCategory.FUNDAMENTAL_ANALYSIS,
                difficulty=DifficultyLevel.INTERMEDIATE,
            ),
        ],
    ),

    # 8. Advanced - Portfolio Management
    CourseDetail(
        id="course-portfolio-management",
        title="Modern Portfolio Management & Asset Allocation",
        description="Strategic diversification, sector rotation across Indian cyclicals/defensives, periodic rebalancing, and correlation risk mitigation.",
        difficulty=DifficultyLevel.ADVANCED,
        category=LearningCategory.PORTFOLIO_MANAGEMENT,
        estimated_duration="45 mins",
        lesson_count=2,
        learning_objectives=[
            "Design balanced multi-asset portfolios across large-cap, mid-cap, and fixed income.",
            "Execute disciplined rebalancing to manage beta and systemic risk.",
        ],
        prerequisites=["course-fundamental-analysis"],
        lessons=[
            LessonSummary(
                id="lesson-asset-allocation",
                course_id="course-portfolio-management",
                title="Asset Allocation & Correlation Matrix",
                order=1,
                duration="20 mins",
                category=LearningCategory.PORTFOLIO_MANAGEMENT,
                difficulty=DifficultyLevel.ADVANCED,
            ),
            LessonSummary(
                id="lesson-rebalancing-strategies",
                course_id="course-portfolio-management",
                title="Portfolio Rebalancing & Sector Rotation",
                order=2,
                duration="25 mins",
                category=LearningCategory.PORTFOLIO_MANAGEMENT,
                difficulty=DifficultyLevel.ADVANCED,
            ),
        ],
    ),
]


# =====================================================================
# LESSONS DATA
# =====================================================================

LESSONS_DATA: List[LessonDetail] = [
    # 1.1 NSE & BSE
    LessonDetail(
        id="lesson-nse-bse-structure",
        course_id="course-market-basics",
        title="NSE, BSE, and Market Ecosystem",
        order=1,
        duration="15 mins",
        category=LearningCategory.STOCK_MARKET_BASICS,
        difficulty=DifficultyLevel.BEGINNER,
        learning_objective="Understand the dual exchange structure of Indian markets (NSE and BSE), regulators (SEBI), and index benchmarks.",
        explanation="India operates primarily through two major recognized stock exchanges: the National Stock Exchange (NSE) founded in 1992, and the Bombay Stock Exchange (BSE) established in 1875. Both exchanges are regulated strictly by the Securities and Exchange Board of India (SEBI). The NSE's flagship index is the NIFTY 50 (representing 50 large-cap bluechip stocks across 13 sectors), while the BSE's flagship index is the SENSEX (30 prominent companies). Trading hours run from 09:15 to 15:30 IST on weekdays, preceded by a pre-open price discovery session between 09:00 and 09:08 IST.",
        key_concepts=[
            "NSE (National Stock Exchange) accounts for majority equity derivatives and cash turnover in India.",
            "BSE (Bombay Stock Exchange) is Asia's oldest exchange and lists over 5,000 publicly traded corporations.",
            "SEBI acts as the autonomous regulatory body protecting retail and institutional investor rights.",
            "Benchmark indices (NIFTY 50 and SENSEX) serve as the barometer of Indian economic sentiment.",
        ],
        examples=[
            LessonExample(
                title="Pre-Open Session Price Discovery",
                context="9:00 AM - 9:08 AM IST on an Indian trading day.",
                scenario="An unexpected interest rate decision was announced overnight. During the pre-open auction from 09:00 to 09:08 IST, buy and sell limit orders are collected without execution. The exchange algorithm calculates an equilibrium price that maximizes traded volume. At 09:08 IST, all matching orders execute at a single discovery price before regular continuous trading starts at 09:15 IST.",
                takeaway="Pre-open equilibrium prevents chaotic wild price swings during market open.",
            )
        ],
        important_notes=[
            "Retail investors can trade the same listed security on either NSE or BSE (e.g. RELIANCE on NSE or BSE).",
            "Indices themselves cannot be bought directly in cash; investors buy ETFs (e.g. NIFTYBEES) or index funds.",
        ],
        common_mistakes=[
            "Assuming stock prices on NSE and BSE must be identical at all split seconds (slight arbitrage spreads exist).",
            "Placing market orders during extreme volatility without checking prevailing market depth.",
        ],
        limitations=[
            "Exchanges may halt individual stocks through upper/lower price bands (circuit filters) to protect market integrity.",
        ],
        illustration_key="market_ecosystem",
        prev_lesson_id=None,
        next_lesson_id="lesson-demat-trading-accounts",
    ),

    # 1.2 Demat & Trading Accounts
    LessonDetail(
        id="lesson-demat-trading-accounts",
        course_id="course-market-basics",
        title="Demat, Trading Accounts & Clearing Mechanics",
        order=2,
        duration="15 mins",
        category=LearningCategory.STOCK_MARKET_BASICS,
        difficulty=DifficultyLevel.BEGINNER,
        learning_objective="Understand how dematerialized shares are held electronically in depositories (CDSL/NSDL) and settled on a T+1 basis.",
        explanation="Trading in India requires a 3-in-1 or linked account structure: a Bank Account (where capital resides), a Trading Account (with a registered stockbroker used to transmit buy/sell orders), and a Demat Account (Dematerialized account with central depositories NSDL or CDSL where your equity shares are stored electronically). In India, equity transactions settle on a rapid T+1 settlement cycle (trade date plus one business day), meaning shares bought on Monday are credited to your Demat account on Tuesday.",
        key_concepts=[
            "Demat accounts hold ownership of shares in electronic form, eliminating physical paper certificates.",
            "CDSL (Central Depository Services Ltd) and NSDL (National Securities Depository Ltd) are India's depositories.",
            "T+1 settlement ensures fast transfer of funds and securities within 24 hours.",
            "Clearing Corporations (NSE Clearing Ltd and Indian Clearing Corporation Ltd) guarantee counterparty settlement.",
        ],
        examples=[
            LessonExample(
                title="Buying 10 Shares of Infosys (INFY)",
                context="A retail investor purchases shares on Wednesday at 11:00 AM IST.",
                scenario="The order executes on the trading account. Funds are debited from the broker margin pool. By Thursday afternoon (T+1), the Clearing Corporation completes settlement and credits 10 units of INFY into the investor's CDSL Demat account.",
                takeaway="The broker executes the order; the depository holds the actual legal ownership of the asset.",
            )
        ],
        important_notes=[
            "Shares held in your Demat account belong to you even if your broker goes bankrupt.",
            "Dividends are directly credited to the linked Bank account verified by the depository.",
        ],
        common_mistakes=[
            "Confusing the trading broker with the depository (Demat custodian).",
            "Failing to authorize e-DIS (Electronic Delivery Instruction Slip) verification when selling Demat holdings.",
        ],
        limitations=[
            "Settlement holidays and weekend days pause the T+1 clock until the next clearing day.",
        ],
        illustration_key="demat_clearing_flow",
        prev_lesson_id="lesson-nse-bse-structure",
        next_lesson_id="lesson-order-types",
    ),

    # 1.3 Order Types
    LessonDetail(
        id="lesson-order-types",
        course_id="course-market-basics",
        title="Market, Limit, and Stop-Loss Orders",
        order=3,
        duration="15 mins",
        category=LearningCategory.STOCK_MARKET_BASICS,
        difficulty=DifficultyLevel.BEGINNER,
        learning_objective="Differentiate and correctly execute Market orders, Limit orders, Stop-Loss (SL), and Stop-Loss Market (SL-M) orders.",
        explanation="Every order placed on an exchange specifies price and execution conditions. A Market Order instructs the broker to buy or sell immediately at the best currently available price in the order book. A Limit Order specifies the maximum price you are willing to pay (for a buy) or the minimum price you will accept (for a sell). A Stop-Loss Order (SL) remains inactive until a specified Trigger Price is breached, at which point it activates as a limit or market order to cap adverse risk.",
        key_concepts=[
            "Market Order prioritizes immediate execution over price certainty.",
            "Limit Order prioritizes price certainty over execution guarantee.",
            "Stop-Loss Limit (SL-L) requires both a Trigger Price and a Limit Price.",
            "Stop-Loss Market (SL-M) converts into an unconditional market order once the trigger is hit.",
        ],
        examples=[
            LessonExample(
                title="Protecting a Breakout Trade with SL-Limit",
                context="You bought Tata Motors at ₹950 expecting a move to ₹1,000.",
                scenario="You do not want to lose more than ₹20 per share. You place a Stop-Loss Limit order with Trigger Price = ₹931 and Limit Price = ₹930. If the price drops to ₹931, the order triggers and will sell your shares at ₹930 or better.",
                takeaway="A predefined stop-loss order enforces objective risk control without emotional hesitation.",
            )
        ],
        important_notes=[
            "During flash crashes or low liquidity, an SL-Limit order may get skipped if price gaps straight down past your limit.",
            "Limit orders remain valid only for the active trading day unless placed as GTT (Good-Till-Triggered).",
        ],
        common_mistakes=[
            "Using market orders on illiquid small-cap stocks, resulting in severe slippage.",
            "Setting the trigger price and limit price too close together during volatile announcements.",
        ],
        limitations=[
            "Orders cannot be modified or canceled once filled by the matching engine.",
        ],
        illustration_key="order_types_comparison",
        prev_lesson_id="lesson-demat-trading-accounts",
        next_lesson_id="lesson-market-terminology",
    ),

    # 1.4 Market Terminology
    LessonDetail(
        id="lesson-market-terminology",
        course_id="course-market-basics",
        title="Essential Market Terminology & Circuit Breakers",
        order=4,
        duration="15 mins",
        category=LearningCategory.STOCK_MARKET_BASICS,
        difficulty=DifficultyLevel.BEGINNER,
        learning_objective="Master key trading vocabulary including Bid/Ask spread, Market Depth, Upper/Lower Circuits, and Volume.",
        explanation="Financial markets operate on specialized terminology. The Bid represents the highest price buyers are willing to pay, while the Ask (Offer) is the lowest price sellers will accept; the difference between them is the Bid-Ask Spread. The Market Depth window displays the top 5 bids and asks. To prevent panic selling or unchecked speculative bubbles, SEBI mandates Price Bands (Circuit Filters) of 2%, 5%, 10%, or 20% on individual stocks. For benchmark indices, market-wide circuit breakers (at 10%, 15%, and 20%) halt trading nationwide for specified cooling periods.",
        key_concepts=[
            "Bid-Ask Spread reflects liquidity; narrower spreads indicate high institutional liquidity.",
            "Market Depth shows real-time supply and demand queue sizes.",
            "Circuit Filters temporarily or daily freeze trading when extreme percentage limits are touched.",
            "Face Value is the nominal value of a share, distinct from its traded Market Price.",
        ],
        examples=[
            LessonExample(
                title="Stock Hitting 10% Upper Circuit",
                context="Mid-cap stock receives major regulatory approval.",
                scenario="Buyers overwhelm sellers. The stock surges by +10% to touch its Upper Circuit limit of ₹220. At this price, only buy orders exist in the depth queue, with zero sellers willing to transact. Trading halts at ₹220 for the remainder of the session unless sellers enter.",
                takeaway="Circuit limits cap daily extreme volatility to prevent speculative stampedes.",
            )
        ],
        important_notes=[
            "F&O (Futures & Options) constituent stocks do not have fixed percentage daily price bands, but have flexing dynamic bands.",
        ],
        common_mistakes=[
            "Mistaking high nominal price (e.g. MRF at ₹1,30,000) for high valuation.",
            "Attempting to sell a stock trapped in a Lower Circuit where zero buyers exist.",
        ],
        limitations=[
            "Orders cannot execute when a stock is locked in a circuit limit without opposing liquidity.",
        ],
        illustration_key="bid_ask_depth",
        prev_lesson_id="lesson-order-types",
        next_lesson_id=None,
    ),

    # 2.1 Candlestick Anatomy & Doji
    LessonDetail(
        id="lesson-candle-anatomy-doji",
        course_id="course-candlestick-mastery",
        title="Candlestick Anatomy & The Doji Family",
        order=1,
        duration="15 mins",
        category=LearningCategory.CANDLESTICK_PATTERNS,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Understand the four price points of candlestick construction and interpret the Doji equilibrium pattern.",
        explanation="Every Japanese candlestick visually records four essential data points over a chosen timeframe: Open, High, Low, and Close (OHLC). The colored rectangular area between Open and Close is the Real Body (green/white when Close > Open; red/black when Close < Open). The thin lines extending above and below are Upper and Lower Shadows (wicks), representing price rejection extremes. When Open and Close are virtually identical, the body is a thin horizontal line known as a Doji. A Doji reflects indecision and equilibrium between bulls and bears.",
        key_concepts=[
            "Standard Doji: Open and close are almost equal with balanced upper and lower shadows.",
            "Long-Legged Doji: High volatility with long upper and lower shadows, showing fierce struggle.",
            "Dragonfly Doji: Long lower shadow with open/close at the session high; signals rejection of lower prices.",
            "Gravestone Doji: Long upper shadow with open/close at the session low; signals rejection of higher prices.",
        ],
        examples=[
            LessonExample(
                title="Dragonfly Doji at Major Support",
                context="NIFTY 50 declining towards the 200-day moving average.",
                scenario="Sellers push the market down early in the session, but institutional buyers step in aggressively in the afternoon, pushing the closing price back up to equal the open. The resulting Dragonfly Doji signals that bears lost control at the support level.",
                takeaway="A Doji is an alert of potential pause or exhaustion, not an automatic buy or sell signal.",
            )
        ],
        important_notes=[
            "A Doji in a choppy, sideways market holds minimal statistical significance.",
            "Always wait for the subsequent candle to confirm direction before taking action.",
        ],
        common_mistakes=[
            "Immediately buying on a Doji without waiting for confirmation above the high.",
            "Ignoring the broader trend context in which the Doji appears.",
        ],
        limitations=[
            "Dojis do not guarantee a reversal; price can easily consolidate and continue in the original trend.",
        ],
        illustration_key="pattern_doji",
        prev_lesson_id=None,
        next_lesson_id="lesson-hammer-shooting-star",
    ),

    # 2.2 Hammer, Inverted Hammer, Shooting Star, Hanging Man
    LessonDetail(
        id="lesson-hammer-shooting-star",
        course_id="course-candlestick-mastery",
        title="Hammer, Inverted Hammer, Shooting Star & Hanging Man",
        order=2,
        duration="20 mins",
        category=LearningCategory.CANDLESTICK_PATTERNS,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Master four core single-candle patterns defined by small real bodies and long shadows on one side.",
        explanation="These four patterns share a similar physical anatomy—a small real body located at one extreme and a shadow at least twice the length of the body—but their interpretation depends entirely on the prior trend. A Hammer occurs at the bottom of a downtrend with a long lower shadow (rejection of sellers). An Inverted Hammer also appears after a downtrend with a long upper shadow. Conversely, a Shooting Star appears after an uptrend with a long upper shadow, signaling exhaustion of buyers. A Hanging Man appears after an uptrend with a long lower shadow, warning that selling interest is beginning to crack the advance.",
        key_concepts=[
            "Hammer: Bullish reversal after downtrend; lower shadow >= 2x body, little to no upper shadow.",
            "Inverted Hammer: Bullish reversal after downtrend; upper shadow >= 2x body, little lower shadow.",
            "Shooting Star: Bearish reversal after uptrend; upper shadow >= 2x body, little lower shadow.",
            "Hanging Man: Bearish reversal warning after uptrend; lower shadow >= 2x body.",
        ],
        examples=[
            LessonExample(
                title="Hammer on Reliance Daily Chart",
                context="Stock corrected 8% over 6 consecutive trading sessions.",
                scenario="During the session, sellers drove Reliance down to ₹2,800. Buyers absorbed all supply and drove price back to close at ₹2,870 near the day's high. The next day opens higher and breaks above ₹2,875 with expanding volume, confirming the Hammer reversal.",
                takeaway="The long lower wick demonstrates decisive institutional absorption of selling pressure.",
            )
        ],
        important_notes=[
            "The color of the Hammer body is secondary, but a green body provides slightly stronger bullish bias.",
            "Shooting Star patterns require strict invalidation stops placed above the pattern's high wick.",
        ],
        common_mistakes=[
            "Calling a candle a Hammer when it appears in the middle of a sideways consolidation.",
            "Entering before the candle period has officially closed.",
        ],
        limitations=[
            "Single-candle patterns are vulnerable to market noise on short intraday timeframes (1m/5m).",
        ],
        illustration_key="pattern_hammer_shooting_star",
        prev_lesson_id="lesson-candle-anatomy-doji",
        next_lesson_id="lesson-engulfing-patterns",
    ),

    # 2.3 Bullish & Bearish Engulfing
    LessonDetail(
        id="lesson-engulfing-patterns",
        course_id="course-candlestick-mastery",
        title="Bullish & Bearish Engulfing Formations",
        order=3,
        duration="20 mins",
        category=LearningCategory.CANDLESTICK_PATTERNS,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Identify and trade high-probability dual-candle Engulfing reversal formations.",
        explanation="Engulfing patterns consist of two contrasting candles where the second candle's real body completely swallows (engulfs) the real body of the first. In a Bullish Engulfing setup, a small red candle during a downtrend is followed by a tall green candle that opens lower than the previous close and aggressively closes well above the previous open. In a Bearish Engulfing setup, a small green candle during an uptrend is completely engulfed by a tall red candle, signaling that aggressive sellers have seized total control of the session.",
        key_concepts=[
            "Bullish Engulfing: Second green candle body completely covers first red candle body.",
            "Bearish Engulfing: Second red candle body completely covers first green candle body.",
            "Volume confirmation: The engulfing candle should ideally print higher volume than previous candles.",
            "Location context: Strongest when forming at key support/resistance or structural swing levels.",
        ],
        examples=[
            LessonExample(
                title="Bearish Engulfing at All-Time Highs",
                context="Bank Nifty rallies 1,200 points to touch 52,000 resistance.",
                scenario="Day 1 prints a modest green candle. Day 2 opens with a gap up, but instantly meets heavy profit taking, closing 400 points lower and completely enveloping Day 1's entire body with surging volume.",
                takeaway="Bearish Engulfing marks a decisive change of character from buyer euphoria to institutional selling.",
            )
        ],
        important_notes=[
            "Shadows do not necessarily need to be engulfed; standard Japanese literature specifies the real body.",
            "Higher timeframe engulfing candles (Weekly/Daily) carry significantly higher win rates than intraday.",
        ],
        common_mistakes=[
            "Shorting immediately into strong support without checking higher timeframe trend alignment.",
        ],
        limitations=[
            "A large engulfing candle can sometimes make the stop-loss distance too wide for favorable risk/reward.",
        ],
        illustration_key="pattern_engulfing",
        prev_lesson_id="lesson-hammer-shooting-star",
        next_lesson_id="lesson-piercing-dark-cloud",
    ),

    # 2.4 Piercing Pattern & Dark Cloud Cover
    LessonDetail(
        id="lesson-piercing-dark-cloud",
        course_id="course-candlestick-mastery",
        title="Piercing Pattern & Dark Cloud Cover",
        order=4,
        duration="15 mins",
        category=LearningCategory.CANDLESTICK_PATTERNS,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Recognize and interpret the Piercing Pattern and Dark Cloud Cover dual-candle formations.",
        explanation="Piercing Pattern and Dark Cloud Cover are close cousins of the engulfing family. A Piercing Pattern is a bullish reversal appearing in a downtrend: Candle 1 is a long red candle; Candle 2 gaps down at the open, but buyers rally price to close more than 50% into Candle 1's real body. Conversely, Dark Cloud Cover is a bearish reversal occurring after an uptrend: Candle 1 is a long green candle; Candle 2 gaps up at the open, but bears push price to close more than 50% down into Candle 1's body.",
        key_concepts=[
            "Piercing Pattern requires Candle 2 to penetrate at least 50% into Candle 1's red body.",
            "Dark Cloud Cover requires Candle 2 to penetrate at least 50% into Candle 1's green body.",
            "Failure to pierce 50% reduces pattern reliability and suggests continuation rather than reversal.",
        ],
        examples=[
            LessonExample(
                title="Piercing Pattern on ICICI Bank",
                context="Stock in 4-day pullback to rising 50-day EMA.",
                scenario="Day 1 is a dark red candle. Day 2 gaps down 1% at the open, but strong institutional buying lifts price through the session to close 65% above the midpoint of Day 1's body.",
                takeaway="Piercing more than 50% indicates that buyers successfully repelled lower price discovery.",
            )
        ],
        important_notes=[
            "If Candle 2 closes completely above Candle 1's open, it becomes a full Bullish Engulfing pattern.",
        ],
        common_mistakes=[
            "Trading the pattern when Candle 2 closes below the 50% midpoint.",
        ],
        limitations=[
            "In modern electronic markets with minimal overnight gaps, strict gap requirements are rarer on intraday charts.",
        ],
        illustration_key="pattern_piercing_dark_cloud",
        prev_lesson_id="lesson-engulfing-patterns",
        next_lesson_id="lesson-stars-soldiers-crows",
    ),

    # 2.5 Morning/Evening Star, Three White Soldiers, Three Black Crows
    LessonDetail(
        id="lesson-stars-soldiers-crows",
        course_id="course-candlestick-mastery",
        title="Morning Star, Evening Star, Three Soldiers & Crows",
        order=5,
        duration="20 mins",
        category=LearningCategory.CANDLESTICK_PATTERNS,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Master 3-candle confirmation patterns: Morning Star, Evening Star, Three White Soldiers, and Three Black Crows.",
        explanation="Three-candle patterns provide built-in confirmation within the formation itself. Morning Star is a 3-candle bullish reversal: tall red candle (bearish momentum), small body candle (indecision star), followed by a tall green candle closing well into Candle 1 (bulls take over). Evening Star is its bearish mirror image. Three White Soldiers consists of three consecutive long green candles, each opening within the previous real body and closing near its high, signaling strong sustained buying. Three Black Crows consists of three consecutive long red candles, signaling persistent institutional distribution.",
        key_concepts=[
            "Morning Star: Bearish candle &rarr; Star &rarr; Bullish candle; classic multi-day bottom reversal.",
            "Evening Star: Bullish candle &rarr; Star &rarr; Bearish candle; classic multi-day top reversal.",
            "Three White Soldiers: Three strong advancing green candles indicating steady accumulation.",
            "Three Black Crows: Three declining red candles with low wicks indicating decisive liquidation.",
        ],
        examples=[
            LessonExample(
                title="Morning Star on NIFTY Daily",
                context="Index correction finds support at prior swing high.",
                scenario="Monday: -1.2% red candle. Tuesday: Narrow-range Doji star. Wednesday: Strong +1.5% green candle closing above Monday's midpoint. The Morning Star confirms the bottom.",
                takeaway="The three-phase progression (panic &rarr; indecision &rarr; resolution) gives stars high predictive reliability.",
            )
        ],
        important_notes=[
            "Three White Soldiers that look overextended or print large upper wicks can indicate exhaustion rather than strength.",
        ],
        common_mistakes=[
            "Chasing Three White Soldiers without waiting for a healthy pullback to manage stop-loss risk.",
        ],
        limitations=[
            "Because three candles are required, by the time the pattern completes, price may already be far from the initial low.",
        ],
        illustration_key="pattern_stars_soldiers_crows",
        prev_lesson_id="lesson-piercing-dark-cloud",
        next_lesson_id=None,
    ),

    # 3.1 Horizontal Levels
    LessonDetail(
        id="lesson-horizontal-levels",
        course_id="course-support-resistance",
        title="Horizontal Demand & Supply Zones",
        order=1,
        duration="15 mins",
        category=LearningCategory.SUPPORT_AND_RESISTANCE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Identify and draw high-probability horizontal support and resistance zones using historical price memory.",
        explanation="Support and Resistance are foundational technical concepts. Support is a price level where buying interest is strong enough to overcome selling pressure, halting a downtrend and prompting a bounce. Resistance is a price ceiling where selling pressure overcomes buying interest, capping further price advance. In professional analysis, these levels are treated as Zones (ranges of price liquidity) rather than razor-thin exact numbers.",
        key_concepts=[
            "Support: Price level or zone where buyers historically outmatch sellers.",
            "Resistance: Price level or zone where sellers historically outmatch buyers.",
            "Touch count: Levels tested 2 to 3 times gain validity, but excessive tests eventually weaken the level.",
            "Zones vs Lines: Drawing horizontal zones accounts for institutional order block dispersion.",
        ],
        examples=[
            LessonExample(
                title="Support Zone on State Bank of India (SBIN)",
                context="SBIN repeatedly bounces between ₹740 and ₹745 over three months.",
                scenario="Whenever price enters the ₹740-₹745 band, large institutional buy orders absorb sellers. Traders treat this entire ₹5 range as an institutional demand zone.",
                takeaway="Treat levels as price regions rather than single digits.",
            )
        ],
        important_notes=[
            "Round psychological numbers (e.g. ₹1,000, ₹500, 25,000 on NIFTY) naturally act as magnet support/resistance.",
        ],
        common_mistakes=[
            "Placing orders precisely at the exact previous low instead of leaving room for liquidity sweeps.",
        ],
        limitations=[
            "Levels are not permanent; every support level will eventually break given sufficient fundamental catalysts.",
        ],
        illustration_key="support_resistance_zones",
        prev_lesson_id=None,
        next_lesson_id="lesson-dynamic-trendlines",
    ),

    # 3.2 Dynamic Trendlines
    LessonDetail(
        id="lesson-dynamic-trendlines",
        course_id="course-support-resistance",
        title="Dynamic Trendlines & Channels",
        order=2,
        duration="15 mins",
        category=LearningCategory.SUPPORT_AND_RESISTANCE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Construct accurate trendlines and parallel price channels to identify prevailing market momentum.",
        explanation="While horizontal levels represent static price memory, Trendlines represent dynamic support or resistance over time. An Ascending Trendline is drawn by connecting at least two (ideally three or more) consecutive higher swing lows. A Descending Trendline connects lower swing highs. When a parallel line is projected along the opposite swing extremes, it forms a Trend Channel, framing the boundaries of the trend.",
        key_concepts=[
            "Ascending Trendline: Acts as dynamic support in an uptrend (Higher Lows).",
            "Descending Trendline: Acts as dynamic resistance in a downtrend (Lower Highs).",
            "Anchor points: Requires at least 2 validated swing pivots, confirmed on the 3rd touch.",
            "Angle of slope: Moderate slopes (30°-45°) are more sustainable than steep unsustainable parabolic slopes.",
        ],
        examples=[
            LessonExample(
                title="Ascending Channel on L&T",
                context="Stock advancing steadily over 6 months.",
                scenario="Every touch of the lower trendline coincides with RSI bouncing from 45, offering systematic trend-following entries. The upper channel line signals where to take partial profits.",
                takeaway="Channels define both high-probability entry zones and objective exit targets.",
            )
        ],
        important_notes=[
            "Do not force trendlines through candle bodies; connect either all wicks or all closes consistently.",
        ],
        common_mistakes=[
            "Redrawing trendlines every few minutes to fit a losing trade thesis.",
        ],
        limitations=[
            "Trendline placement contains an element of subjective chartist interpretation.",
        ],
        illustration_key="trendlines_channels",
        prev_lesson_id="lesson-horizontal-levels",
        next_lesson_id="lesson-role-reversal-breakouts",
    ),

    # 3.3 Role Reversal, Breakouts & Fakeouts
    LessonDetail(
        id="lesson-role-reversal-breakouts",
        course_id="course-support-resistance",
        title="Role Reversal, Breakouts & Fakeouts",
        order=3,
        duration="20 mins",
        category=LearningCategory.SUPPORT_AND_RESISTANCE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Master the role reversal principle and detect false breakout traps (bull/bear traps).",
        explanation="When a key resistance level is decisively breached by price, that level undergoes a Role Reversal and becomes future support on any subsequent pullback. Similarly, broken support transforms into overhead resistance. However, retail traders frequently get trapped by False Breakouts (fakeouts), where price briefly pokes beyond a level to trigger stop orders before abruptly reversing back inside the range.",
        key_concepts=[
            "Role Reversal: Old Resistance becomes New Support; Old Support becomes New Resistance.",
            "True Breakout criteria: Decisive close outside the zone, accompanied by 1.5x-2x average volume.",
            "Fakeout (Bull Trap): Price breaks resistance, lures buyers, and quickly plunges back below.",
            "Retest Entry: Entering on the pullback to the broken level offers superior risk/reward compared to chasing.",
        ],
        examples=[
            LessonExample(
                title="NIFTY Retest of 24,000 Breakout",
                context="NIFTY was capped at 24,000 for three weeks.",
                scenario="NIFTY breaks above 24,000 with heavy volume, reaches 24,150, and then pulls back to test 24,010. Buyers step in decisively, turning the old resistance into firm support and driving price toward 24,400.",
                takeaway="Waiting for the retest avoids chasing breakouts and provides a clear invalidation level.",
            )
        ],
        important_notes=[
            "Volume is the ultimate discriminator between a legitimate breakout and an institutional liquidity trap.",
        ],
        common_mistakes=[
            "Buying the instant a candle wicks above resistance before the candle has closed.",
        ],
        limitations=[
            "In very powerful momentum trends, price may never pull back for a clean retest.",
        ],
        illustration_key="breakout_role_reversal",
        prev_lesson_id="lesson-dynamic-trendlines",
        next_lesson_id=None,
    ),

    # 4.1 RSI Indicator
    LessonDetail(
        id="lesson-rsi-indicator",
        course_id="course-technical-indicators",
        title="RSI: Momentum, Extremes & Divergences",
        order=1,
        duration="20 mins",
        category=LearningCategory.RSI_INDICATOR,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Calculate, interpret, and trade with the Relative Strength Index (RSI 14) without falling into overbought traps.",
        explanation="Developed by J. Welles Wilder, the Relative Strength Index (RSI) is a bounded momentum oscillator that fluctuates between 0 and 100. It measures the velocity and magnitude of recent price gains relative to recent losses over a standard 14-period lookback. Traditionally, readings above 70 indicate 'overbought' conditions, while readings below 30 indicate 'oversold'. Crucially, in strong trending markets, RSI can remain pegged above 70 or below 30 for weeks. The most potent signal is RSI Divergence: when price makes a higher high, but RSI makes a lower high (Bearish Divergence), signaling fading internal momentum.",
        key_concepts=[
            "Formula Concept: RSI = 100 - [100 / (1 + RS)], where RS is Average Gain / Average Loss.",
            "Bullish Range Rules: In a strong uptrend, RSI typically oscillates between 40 and 80 (40 acts as support).",
            "Bearish Range Rules: In a downtrend, RSI typically oscillates between 20 and 60 (60 acts as resistance).",
            "Regular Bullish Divergence: Price makes a Lower Low, but RSI makes a Higher Low (reversal warning).",
            "Regular Bearish Divergence: Price makes a Higher High, but RSI makes a Lower High (exhaustion warning).",
        ],
        examples=[
            LessonExample(
                title="Bearish RSI Divergence on Bajaj Finance",
                context="Stock rallies from ₹6,800 to ₹7,400.",
                scenario="Price reaches ₹7,200 with RSI at 78. After a brief consolidation, price makes a higher high at ₹7,400, but RSI only reaches 66. This clear bearish divergence warns that buying momentum is drying up, preceding an 8% correction.",
                takeaway="Divergence signals internal momentum exhaustion before price itself breaks support.",
            )
        ],
        important_notes=[
            "Never short a stock simply because RSI is above 70; institutional momentum leaders often sustain high RSI readings.",
        ],
        common_mistakes=[
            "Blindly buying when RSI hits 29 in a collapsing downtrend without waiting for divergence or price reversal.",
        ],
        limitations=[
            "Divergences can persist for multiple swings in powerful trending markets before price actually reverses.",
        ],
        illustration_key="indicator_rsi_divergence",
        prev_lesson_id=None,
        next_lesson_id="lesson-macd-indicator",
    ),

    # 4.2 MACD Indicator
    LessonDetail(
        id="lesson-macd-indicator",
        course_id="course-technical-indicators",
        title="MACD: Line Crossovers, Histogram & Momentum",
        order=2,
        duration="20 mins",
        category=LearningCategory.MACD_INDICATOR,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Understand the three components of MACD (MACD line, Signal line, Histogram) and identify momentum shifts.",
        explanation="Created by Gerald Appel, the Moving Average Convergence Divergence (MACD) is both a trend-following and momentum indicator. It comprises three elements: 1) The MACD Line (the difference between the 12-day EMA and 26-day EMA); 2) The Signal Line (a 9-day EMA of the MACD Line); and 3) The MACD Histogram (the mathematical distance between the MACD Line and the Signal Line). When the MACD line crosses above the Signal line, it produces a Bullish Crossover. When the Histogram changes color and shrinks towards the zero line, it signals that current momentum is decelerating.",
        key_concepts=[
            "MACD Line = 12 EMA - 26 EMA.",
            "Signal Line = 9 EMA of the MACD Line.",
            "Histogram = MACD Line - Signal Line.",
            "Zero Line Crossover: When MACD crosses above zero, 12 EMA has surpassed 26 EMA (confirming an uptrend).",
            "Histogram Peak: When histogram bars begin shortening, momentum is waning even before lines cross.",
        ],
        examples=[
            LessonExample(
                title="MACD Bullish Cross with Zero-Line Confirmation",
                context="HDFC Bank consolidating near ₹1,500.",
                scenario="The MACD line crosses above the Signal line below zero. Two sessions later, both lines cross cleanly above the Zero Line, accompanied by green histogram expansion. This confirmed institutional accumulation and preceded a 100-point rally.",
                takeaway="Crossovers above the zero line carry higher trend-continuation probability.",
            )
        ],
        important_notes=[
            "Because MACD is derived from moving averages, it is inherently a lagging indicator.",
        ],
        common_mistakes=[
            "Trading every MACD crossover in a flat, range-bound market, resulting in constant whipsaws.",
        ],
        limitations=[
            "Lags real-time turning points; not suitable as a standalone early entry trigger.",
        ],
        illustration_key="indicator_macd_structure",
        prev_lesson_id="lesson-rsi-indicator",
        next_lesson_id="lesson-moving-averages",
    ),

    # 4.3 Moving Averages
    LessonDetail(
        id="lesson-moving-averages",
        course_id="course-technical-indicators",
        title="Moving Averages: SMA, EMA & Golden/Death Crosses",
        order=3,
        duration="15 mins",
        category=LearningCategory.MOVING_AVERAGES,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Differentiate Simple (SMA) and Exponential (EMA) Moving Averages and evaluate institutional Golden and Death Crosses.",
        explanation="A Moving Average smooths price data to create a single trend-following line. A Simple Moving Average (SMA) calculates the unweighted arithmetic mean of closing prices over N periods. An Exponential Moving Average (EMA) applies a multiplier to assign higher weight to recent prices, reducing lag. Key benchmark periods used by institutions include the 20 EMA (short-term momentum), 50 EMA (intermediate trend), and 200 SMA (long-term secular trend). A Golden Cross occurs when the 50-day average crosses above the 200-day average (bullish milestone). A Death Cross occurs when the 50-day crosses below the 200-day (bearish milestone).",
        key_concepts=[
            "EMA reacts faster to recent price spikes; SMA gives equal weight to all historical points in the window.",
            "200-day Moving Average acts as the global institutional benchmark for bull vs. bear regime.",
            "Golden Cross: 50 MA crossing above 200 MA signals long-term bullish structural shift.",
            "Death Cross: 50 MA crossing below 200 MA signals long-term bearish structural shift.",
            "Dynamic Support/Resistance: Pullbacks to the 20 EMA in strong trends often serve as low-risk entry zones.",
        ],
        examples=[
            LessonExample(
                title="NIFTY 50 Golden Cross",
                context="Index recovering after an extended 6-month consolidation.",
                scenario="The 50-day EMA crosses above the 200-day SMA at 21,500. Institutional funds use this cross to increase equity allocations, confirming the continuation of the multi-year bull market.",
                takeaway="Major moving average crossovers confirm structural macroeconomic trends.",
            )
        ],
        important_notes=[
            "Moving averages are trend filters; in a sideways chop, price will repeatedly cross back and forth.",
        ],
        common_mistakes=[
            "Expecting instant explosive moves immediately upon a Golden Cross (it is a lagging confirmation, not an intraday trigger).",
        ],
        limitations=[
            "Can cause significant drawdown if used as an exit signal in sharp trend reversals.",
        ],
        illustration_key="indicator_moving_averages",
        prev_lesson_id="lesson-macd-indicator",
        next_lesson_id="lesson-volume-analysis",
    ),

    # 4.4 Volume Analysis
    LessonDetail(
        id="lesson-volume-analysis",
        course_id="course-technical-indicators",
        title="Volume Analysis: Confirmation, Spikes & Relative Volume",
        order=4,
        duration="20 mins",
        category=LearningCategory.VOLUME_ANALYSIS,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Decode institutional volume footprints, volume confirmation, and volume price divergence.",
        explanation="Volume is the total number of shares transacted during a given period. While price represents what market participants believe, volume represents how much capital is backing that belief. In a healthy uptrend, volume should expand on rising sessions and contract on pullback days. If price reaches a new high on declining volume, it signals weak buyer conviction (Volume Divergence). Relative Volume (RVOL) compares current volume against the average volume for that exact time of day, highlighting genuine institutional activity.",
        key_concepts=[
            "Volume confirms trend: Price Up + Volume Up = Strong Bullish confirmation.",
            "Weakness: Price Up + Volume Down = Fading buying conviction.",
            "Absorption: Massive volume spike with narrow candle body = Institutional supply meeting demand.",
            "Climax Volume: Ultra-high volume after extended rally or crash often signals trend exhaustion.",
        ],
        examples=[
            LessonExample(
                title="Breakout with 3x Relative Volume",
                context="Stock consolidating under ₹500 resistance for 2 months.",
                scenario="Price breaks above ₹500 on 3 times its 20-day average volume within the first hour of trading. This massive surge confirms that institutional algorithms and mutual funds are participating, not just retail traders.",
                takeaway="High volume expansion validates breakout credibility.",
            )
        ],
        important_notes=[
            "Always inspect volume relative to the stock's own 20-day moving average volume.",
        ],
        common_mistakes=[
            "Ignoring volume and trading breakouts based purely on chart lines.",
        ],
        limitations=[
            "Intraday volume at 09:15 and 15:15 is naturally higher due to opening/closing auctions; normalize using RVOL.",
        ],
        illustration_key="indicator_volume_spread",
        prev_lesson_id="lesson-moving-averages",
        next_lesson_id=None,
    ),

    # 5.1 The 1% Rule
    LessonDetail(
        id="lesson-one-percent-rule",
        course_id="course-risk-management",
        title="The 1% Rule & Capital Preservation Formula",
        order=1,
        duration="20 mins",
        category=LearningCategory.RISK_MANAGEMENT,
        difficulty=DifficultyLevel.ADVANCED,
        learning_objective="Implement the golden rule of risk management: never risk more than 1% of total trading capital on a single trade.",
        explanation="The primary objective of a professional trader is not profit maximization, but capital preservation. The 1% Rule dictates that on any individual trade, the maximum financial loss incurred if your stop-loss is triggered must never exceed 1% of your total account equity. If you have an account of ₹5,00,000, your maximum risk per trade is strictly ₹5,000. Risking 5% or 10% per trade mathematically ensures eventual account ruin through inevitable consecutive losing streaks (e.g. 5 consecutive losses at 10% risk depletes over 40% of capital, requiring a 67% gain just to break even).",
        key_concepts=[
            "Max Risk per Trade = Total Account Capital * 0.01.",
            "Position Size does NOT equal Risk; Position Size = (Account Risk in ₹) / (Entry Price - Stop Loss Price).",
            "Asymmetric Recovery Curve: A 50% loss requires a 100% gain to recover; a 20% loss requires only 25%.",
            "Drawdown Circuit Breakers: Halting trading if weekly drawdown reaches 3% protects psychological sanity.",
        ],
        examples=[
            LessonExample(
                title="Applying 1% Risk on a ₹2,00,000 Account",
                context="Trader has ₹2,00,000 total trading capital.",
                scenario="Max allowed loss = 1% of ₹2,00,000 = ₹2,000. Stock XYZ is trading at ₹400 with technical stop-loss at ₹380 (risk per share = ₹20). Max Quantity = ₹2,000 / ₹20 = 100 shares. Total capital allocated = 100 * ₹400 = ₹40,000. If stopped out, the loss is exactly ₹2,000 (1%).",
                takeaway="Position size is derived strictly from risk and stop distance, never chosen arbitrarily.",
            )
        ],
        important_notes=[
            "The 1% rule scales automatically: as account grows, rupee risk expands; as account draws down, rupee risk contracts.",
        ],
        common_mistakes=[
            "Confusing 'allocating 1% of capital' with 'risking 1% of capital'.",
            "Increasing position size during a losing streak to 'make it back quickly' (revenge trading).",
        ],
        limitations=[
            "Requires discipline to accept smaller quantity on volatile stocks with wide technical stop losses.",
        ],
        illustration_key="risk_one_percent_math",
        prev_lesson_id=None,
        next_lesson_id="lesson-position-sizing-inr",
    ),

    # 5.2 Position Sizing & Stop-Loss Placement
    LessonDetail(
        id="lesson-position-sizing-inr",
        course_id="course-risk-management",
        title="Exact Position Sizing & Stop-Loss Placement (INR)",
        order=2,
        duration="20 mins",
        category=LearningCategory.RISK_MANAGEMENT,
        difficulty=DifficultyLevel.ADVANCED,
        learning_objective="Master technical stop-loss placement based on market structure and calculate exact share quantities in INR.",
        explanation="A stop-loss must never be placed at an arbitrary dollar or rupee figure. It must be placed at a technical invalidation level—a price point where your trade hypothesis is objectively proven wrong (e.g. below a validated swing low, below a key moving average, or below a breakout consolidation base). Once the technical stop price is determined, the distance from your entry price defines your Risk Per Share. Dividing your total allowed monetary risk by the Risk Per Share gives the exact number of shares to purchase.",
        key_concepts=[
            "Invalidation Level: The price where your reason for entering the trade no longer exists.",
            "Technical Stops: Placed beyond market structure (e.g. 2 ticks below swing low or ATR buffer).",
            "Quantity Formula = (Portfolio Value * Risk Percentage) / |Entry Price - Stop Loss Price|.",
            "Average True Range (ATR) Stops: Placing stops 1.5x to 2x ATR away prevents premature stop-outs from normal market noise.",
        ],
        examples=[
            LessonExample(
                title="Position Sizing on TCS Breakout",
                context="Account Equity: ₹10,00,000. Risk parameter: 1% (₹10,000).",
                scenario="TCS breaks out at ₹4,200. Structural swing low is at ₹4,150. Risk per share = ₹4,200 - ₹4,150 = ₹50. Position size = ₹10,000 / ₹50 = 200 shares. Total position value = 200 * ₹4,200 = ₹8,40,000.",
                takeaway="The math guarantees that whether stopped out on TCS or a penny stock, you only lose your planned 1%.",
            )
        ],
        important_notes=[
            "Never move your stop-loss further away once a trade is live; you may only trail it forward to protect gains.",
        ],
        common_mistakes=[
            "Placing stop losses too tight to buy bigger position sizes, leading to constant whipsaws.",
        ],
        limitations=[
            "Overnight gap openings can execute beyond your stop price, creating slippage in high-impact events.",
        ],
        illustration_key="position_sizing_calc",
        prev_lesson_id="lesson-one-percent-rule",
        next_lesson_id="lesson-risk-reward-expectancy",
    ),

    # 5.3 Risk-to-Reward & Mathematical Expectancy
    LessonDetail(
        id="lesson-risk-reward-expectancy",
        course_id="course-risk-management",
        title="Risk-to-Reward Ratio & Mathematical Expectancy",
        order=3,
        duration="20 mins",
        category=LearningCategory.RISK_MANAGEMENT,
        difficulty=DifficultyLevel.ADVANCED,
        learning_objective="Calculate trade expectancy and understand why high win-rate is not required for profitability with 1:2+ R:R.",
        explanation="Profitable trading is an exercise in probability and expectancy, not prediction. Risk-to-Reward (R:R) compares the potential loss to the potential reward. With a 1:2 R:R ratio, you risk ₹1,000 to make ₹2,000. With a 1:2 R:R, a trader needs only a 34% win rate to break even. At a modest 45% win rate, a 1:2 system produces substantial long-term wealth. Expectancy Formula: E = (Win Rate * Average Win) - (Loss Rate * Average Loss). A positive expectancy system combined with strict risk sizing guarantees long-term edge.",
        key_concepts=[
            "Minimum 1:2 R:R ensures you make twice as much on winners as you lose on losers.",
            "Expectancy = (Win% * Avg Win) - (Loss% * Avg Loss).",
            "Win Rate fallacy: A system with an 85% win rate can still blow up if the 15% losses are catastrophic.",
            "Asymmetric Risk: Targeting trades with defined structural targets yielding 1:3 or 1:4 R:R.",
        ],
        examples=[
            LessonExample(
                title="100 Trades Comparison",
                context="Two traders complete 100 trades with ₹5,000 risk per trade.",
                scenario="Trader A has a 70% win rate with 1:0.5 R:R: Wins 70 * ₹2,500 = ₹1,75,000; Loses 30 * ₹5,000 = ₹1,50,000. Net profit = ₹25,000. Trader B has only a 40% win rate with 1:2.5 R:R: Wins 40 * ₹12,500 = ₹5,00,000; Loses 60 * ₹5,000 = ₹3,00,000. Net profit = ₹2,00,000. Trader B wins 8x more money despite being wrong on 60% of trades.",
                takeaway="R:R asymmetry drives trading profits, not being right on every single trade.",
            )
        ],
        important_notes=[
            "Ensure the profit target is based on realistic technical resistance, not arbitrary wishful thinking.",
        ],
        common_mistakes=[
            "Cutting winning trades prematurely for small gains while letting losing trades run to full stop-loss.",
        ],
        limitations=[
            "Higher R:R targets naturally result in lower win rates; traders must be psychologically prepared for losing runs.",
        ],
        illustration_key="expectancy_matrix",
        prev_lesson_id="lesson-position-sizing-inr",
        next_lesson_id=None,
    ),

    # 6.1 Trading Psychology
    LessonDetail(
        id="lesson-trading-psychology",
        course_id="course-psychology-strategy",
        title="Mastering Trading Psychology & Emotional Discipline",
        order=1,
        duration="20 mins",
        category=LearningCategory.TRADING_PSYCHOLOGY,
        difficulty=DifficultyLevel.ADVANCED,
        learning_objective="Identify and conquer psychological pitfalls: FOMO, revenge trading, greed, fear of missing out, and outcome bias.",
        explanation="Mark Douglas, author of Trading in the Zone, observed that 90% of trading performance is mental. The human brain evolved to seek certainty and avoid danger, but financial markets are fundamentally uncertain probabilistic environments. Emotional trading manifests as Fear of Missing Out (FOMO)—chasing vertical green candles; Loss Aversion—refusing to take a small loss until it becomes catastrophic; and Revenge Trading—doubling down immediately after a loss to satisfy ego. Professional traders treat each trade as simply one instance in a series of hundreds of probabilistic outcomes.",
        key_concepts=[
            "Probabilistic Thinking: Anything can happen on any given trade; your edge reveals itself over large sample sizes.",
            "FOMO Control: The market will always offer another setup; missed opportunities cost ₹0.",
            "Acceptance of Loss: A stop-loss is simply the routine cost of doing business, like electricity for a shop.",
            "Trading Journal: Recording emotional state, setup thesis, and execution errors is mandatory for improvement.",
        ],
        examples=[
            LessonExample(
                title="Stopping Revenge Trading via Daily Loss Limit",
                context="Trader takes two consecutive losses in the morning totaling ₹4,000.",
                scenario="Feeling angry and frustrated, the trader feels an urge to jump into an unverified mid-cap rally. Instead, having set a hard daily loss limit of ₹4,000, the trading terminal automatically shuts down. The mid-cap stock crashes 30 minutes later. The rule saved ₹20,000 of emotional damage.",
                takeaway="Rules-based system constraints protect capital when emotional discipline fails.",
            )
        ],
        important_notes=[
            "Never trade when sleep-deprived, stressed, or experiencing major personal distress.",
        ],
        common_mistakes=[
            "Measuring trade quality solely by its outcome rather than whether you followed your plan (Outcome Bias).",
        ],
        limitations=[
            "Psychological discipline cannot compensate for an unviable trading system without mathematical edge.",
        ],
        illustration_key="psychology_cycle",
        prev_lesson_id=None,
        next_lesson_id="lesson-multi-timeframe-analysis",
    ),

    # 6.2 Multiple Timeframe Analysis
    LessonDetail(
        id="lesson-multi-timeframe-analysis",
        course_id="course-psychology-strategy",
        title="Multiple Timeframe Analysis & Market Confluence",
        order=2,
        duration="20 mins",
        category=LearningCategory.SWING_TRADING,
        difficulty=DifficultyLevel.ADVANCED,
        learning_objective="Align Monthly, Weekly, Daily, and Intraday charts to execute high-confluence swing trades.",
        explanation="Multiple Timeframe Analysis (MTFA) is the practice of evaluating the same asset across distinct timeframes to ensure you trade with the dominant macro tide rather than against it. A classic rule of thumb uses a factor of 4 to 6 between charts: for example, Monthly (Macro Trend), Weekly (Intermediate Trend/Structure), Daily (Swing Setup), and 60-minute/15-minute (Precision Entry Trigger). Trading in the direction of the higher timeframe dramatically increases the reliability of candlestick patterns and indicator signals.",
        key_concepts=[
            "Higher timeframe dominance: A daily support level will easily overpower a 5-minute resistance level.",
            "Macro trend filter: If the Weekly chart is in a firm downtrend, ignore long signals on the 15-minute chart.",
            "Confluence: When a horizontal support, dynamic trendline, and 50 EMA all align at the same price zone.",
            "Top-Down Approach: Start from Monthly/Weekly &rarr; move to Daily &rarr; execute on Hourly.",
        ],
        examples=[
            LessonExample(
                title="Confluence Setup on Bharti Airtel",
                context="Weekly chart shows strong multi-year uptrend.",
                scenario="Price pulls back to ₹1,400 on the Daily chart. At ₹1,400, three independent factors align: 1) Prior major swing high resistance turned support; 2) The rising 50-day EMA; 3) 61.8% Fibonacci retracement. The 1-hour chart prints a Bullish Engulfing pattern. The trade triggers with high confluence.",
                takeaway="Confluence stacks probabilities in your favor.",
            )
        ],
        important_notes=[
            "Do not analyze too many timeframes (more than 3 or 4 leads to analysis paralysis).",
        ],
        common_mistakes=[
            "Taking counter-trend intraday scalps against a powerful multi-month institutional trend.",
        ],
        limitations=[
            "Higher timeframe trends can take months to shift, requiring patience from swing traders.",
        ],
        illustration_key="multi_timeframe_alignment",
        prev_lesson_id="lesson-trading-psychology",
        next_lesson_id="lesson-portfolio-investing",
    ),

    # 6.3 Long-Term Investing & Portfolio Diversification
    LessonDetail(
        id="lesson-portfolio-investing",
        course_id="course-psychology-strategy",
        title="Long-Term Investing & Portfolio Diversification",
        order=3,
        duration="20 mins",
        category=LearningCategory.LONG_TERM_INVESTING,
        difficulty=DifficultyLevel.ADVANCED,
        learning_objective="Harness compounding, asset allocation, and fundamental moat analysis to build generational wealth.",
        explanation="While trading focuses on extracting short-term market inefficiencies through price action, investing focuses on participating in the long-term compounding of India's corporate earnings. Legendary investor Charlie Munger emphasized that the big money is not in the buying and selling, but in the waiting. True long-term wealth creation requires understanding economic moats (competitive advantages), reinvestment rates, compounding mathematics, and uncorrelated asset diversification across equities, gold, and debt.",
        key_concepts=[
            "Compounding: Reinvested earnings generate geometric growth over multi-decade horizons.",
            "Economic Moat: Brand power, high switching costs, network effects, or cost advantages that protect margins.",
            "Asset Allocation: Blending Indian equities, fixed income, and sovereign gold bonds reduces portfolio volatility.",
            "Rupee Cost Averaging (SIP): Systematic regular investing neutralizes the risk of market timing.",
        ],
        examples=[
            LessonExample(
                title="Power of Compounding in Indian Equities",
                context="Monthly SIP of ₹10,000 in NIFTY 50 index over 20 years at historical ~12% CAGR.",
                scenario="Total capital invested = ₹24,00,000. Final portfolio value approximates ₹99,91,479 (nearly ₹1 Crore), where ~₹76 Lakhs represents pure compounding interest generated without forecasting a single daily candle.",
                takeaway="Time in the market consistently beats timing the market for long-term wealth.",
            )
        ],
        important_notes=[
            "Never invest capital in volatile equities if you require the money within the next 3 to 5 years.",
        ],
        common_mistakes=[
            "Treating high-frequency trading and long-term investing with the same emotional approach.",
            "Selling high-quality compounders during routine macroeconomic market corrections.",
        ],
        limitations=[
            "Requires immense patience and emotional fortitude to endure periodic 20-30% market drawdowns.",
        ],
        illustration_key="compounding_diversification",
        prev_lesson_id="lesson-multi-timeframe-analysis",
        next_lesson_id=None,
    ),

    # 7.1 Financial Statements
    LessonDetail(
        id="lesson-financial-statements",
        course_id="course-fundamental-analysis",
        title="Reading Financial Statements & Cash Flows",
        order=1,
        duration="20 mins",
        category=LearningCategory.FUNDAMENTAL_ANALYSIS,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Understand the three primary financial statements: Balance Sheet, Profit & Loss (P&L), and Cash Flow statement.",
        explanation="Fundamental analysis assesses a company's intrinsic financial health. The Profit and Loss Statement reveals revenue, operating costs (EBITDA), and bottom-line Net Profit (PAT) over a quarter or fiscal year. The Balance Sheet provides a snapshot of company Assets (what it owns) versus Liabilities (what it owes) and Shareholder Equity at a specific point in time. The Cash Flow Statement tracks actual cash moving into and out of operating activities, investing activities, and financing activities. Crucially, accounting profits do not equal cash; high Free Cash Flow (FCF) is the hallmark of financial quality.",
        key_concepts=[
            "P&L Statement: Top-line Revenue &rarr; Operating Profit (EBITDA) &rarr; Net Profit (PAT).",
            "Balance Sheet Equation: Assets = Liabilities + Shareholders' Equity.",
            "Cash Flow from Operations (CFO): High CFO relative to PAT validates earnings quality.",
            "Free Cash Flow (FCF) = CFO - Capital Expenditures (CapEx); cash available to pay dividends or reinvest.",
        ],
        examples=[
            LessonExample(
                title="Accounting Profit vs. Cash Flow Trap",
                context="Company ABC reports ₹100 Crore Net Profit but ₹0 Operating Cash Flow.",
                scenario="Investigation reveals all sales were recorded as uncollected Accounts Receivable with aggressive credit terms. The company ran out of liquidity to pay suppliers despite reporting positive accounting profit on paper.",
                takeaway="Always verify that accounting profits are backed by real cash flow from operations.",
            )
        ],
        important_notes=[
            "Auditor notes and contingent liabilities in annual reports often conceal major hidden risks.",
        ],
        common_mistakes=[
            "Focusing solely on revenue growth without checking operating profit margins and cash conversion.",
        ],
        limitations=[
            "Financial statements reflect past quarterly performance and are published with a reporting lag.",
        ],
        illustration_key="financial_statements_flow",
        prev_lesson_id=None,
        next_lesson_id="lesson-valuation-metrics",
    ),

    # 7.2 Valuation Ratios
    LessonDetail(
        id="lesson-valuation-metrics",
        course_id="course-fundamental-analysis",
        title="Core Valuation Ratios: P/E, P/B, ROE & ROCE",
        order=2,
        duration="25 mins",
        category=LearningCategory.FUNDAMENTAL_ANALYSIS,
        difficulty=DifficultyLevel.INTERMEDIATE,
        learning_objective="Evaluate whether a stock is cheap or expensive using P/E, P/B, Return on Equity (ROE), and Return on Capital Employed (ROCE).",
        explanation="Valuation ratios help investors compare companies of different sizes across an industry. Price-to-Earnings (P/E) measures current share price against Earnings Per Share (EPS). Price-to-Book (P/B) measures market price against book value (especially vital for banks and financial institutions). Return on Equity (ROE) measures how effectively management generates profits from shareholder capital, while Return on Capital Employed (ROCE) includes debt capital. High-quality Indian compounders typically sustain ROCE and ROE above 18-20% through economic cycles.",
        key_concepts=[
            "P/E Ratio = Market Price / EPS. Must be compared against historical average and industry peers.",
            "P/B Ratio = Market Price / Book Value Per Share.",
            "ROE = Net Income / Shareholders' Equity.",
            "ROCE = EBIT / (Total Assets - Current Liabilities); measures operational capital efficiency.",
            "Debt-to-Equity: Ratios above 1.0 (excluding banking/NBFC) increase bankruptcy risk during downturns.",
        ],
        examples=[
            LessonExample(
                title="Comparing Two FMCG Competitors",
                context="Company A trades at P/E 30 with 25% ROCE. Company B trades at P/E 15 with 8% ROCE.",
                scenario="Company B appears superficially 'cheaper' by P/E, but Company A generates three times more cash per rupee of invested capital, justifying its valuation premium.",
                takeaway="Valuation must always be evaluated in conjunction with return on capital and business quality.",
            )
        ],
        important_notes=[
            "Cyclical commodity companies (steel, chemicals) often trade at single-digit P/Es at the peak of their earnings cycle.",
        ],
        common_mistakes=[
            "Falling into 'Value Traps'—buying low P/E companies whose earnings are collapsing.",
        ],
        limitations=[
            "One-off extraordinary gains can temporarily distort P/E and ROE metrics.",
        ],
        illustration_key="valuation_metrics_radar",
        prev_lesson_id="lesson-financial-statements",
        next_lesson_id=None,
    ),

    # 8.1 Asset Allocation
    LessonDetail(
        id="lesson-asset-allocation",
        course_id="course-portfolio-management",
        title="Asset Allocation & Correlation Matrix",
        order=1,
        duration="20 mins",
        category=LearningCategory.PORTFOLIO_MANAGEMENT,
        difficulty=DifficultyLevel.ADVANCED,
        learning_objective="Structure a resilient multi-asset portfolio with negative or low correlation to optimize the Sharpe Ratio.",
        explanation="Asset allocation determines more than 90% of a portfolio's total return variance. Holding 20 different Indian IT stocks is not diversification—it is concentrated sector risk. True diversification allocates capital across uncorrelated or negatively correlated asset classes: Indian Equities (high growth), Fixed Income/Debt (capital stability), and Gold/Commodities (inflation hedge). Modern Portfolio Theory demonstrates that combining uncorrelated assets shifts the Efficient Frontier, producing higher risk-adjusted returns (Sharpe ratio) with lower maximum drawdowns.",
        key_concepts=[
            "Correlation Coefficient ranges from -1.0 (perfect inverse) to +1.0 (perfect synchrony).",
            "Gold historically exhibits low or negative correlation to Indian equities during market crashes.",
            "Debt/Bonds provide regular yield and dry powder to buy equities during severe market panics.",
            "Sharpe Ratio measures excess return per unit of volatility: (Portfolio Return - Risk Free Rate) / Standard Deviation.",
        ],
        examples=[
            LessonExample(
                title="The 2020 Market Shock Resilience",
                context="Indian equities dropped ~35% in March 2020.",
                scenario="An all-equity portfolio suffered a painful 35% drawdown. A diversified 60/25/15 portfolio (60% Equities, 25% Debt, 15% Gold) experienced only a 18% drawdown, while sovereign gold surged +25%, providing capital to rebalance into cheap equities.",
                takeaway="Uncorrelated asset allocation cushions market shocks and eliminates forced selling.",
            )
        ],
        important_notes=[
            "Asset allocation should match your investment horizon and individual risk tolerance.",
        ],
        common_mistakes=[
            "Over-diversifying into 60+ mutual funds or stocks, creating index-hugging with bloated management fees.",
        ],
        limitations=[
            "During extreme liquidity panics, correlations across risk assets can temporarily spike towards 1.0.",
        ],
        illustration_key="asset_allocation_pie",
        prev_lesson_id=None,
        next_lesson_id="lesson-rebalancing-strategies",
    ),

    # 8.2 Rebalancing Strategies
    LessonDetail(
        id="lesson-rebalancing-strategies",
        course_id="course-portfolio-management",
        title="Portfolio Rebalancing & Sector Rotation",
        order=2,
        duration="25 mins",
        category=LearningCategory.PORTFOLIO_MANAGEMENT,
        difficulty=DifficultyLevel.ADVANCED,
        learning_objective="Execute systematic calendar and threshold rebalancing, and track Indian economic sector rotation.",
        explanation="Over time, high-performing assets grow faster than others, causing your portfolio to drift away from target risk parameters. For instance, after a massive equity bull run, your equity allocation may expand from 60% to 80%, exposing you to excessive crash risk. Rebalancing is the disciplined process of trimming overperforming assets and redeploying proceeds into underperforming assets. This mechanically enforces buying low and selling high without emotion. Furthermore, institutional capital rotates through sectors based on economic cycles (e.g. cyclicals/banks in expansion; FMCG/pharma in slowdowns).",
        key_concepts=[
            "Calendar Rebalancing: Rebalancing on a set periodic schedule (e.g. annually or semi-annually).",
            "Threshold (Tolerance Band) Rebalancing: Rebalancing whenever an asset class deviates by > 5% from target.",
            "Tax Efficiency: Using fresh inflows (SIPs) to rebalance underweighted assets avoids capital gains tax triggers.",
            "Sector Rotation: Capital migrates from early-cycle financials &rarr; mid-cycle industrials &rarr; late-cycle defensives.",
        ],
        examples=[
            LessonExample(
                title="Threshold Rebalancing in Action",
                context="Target allocation: 70% Equity / 30% Debt.",
                scenario="Following a massive equity rally, equity swells to 78% while debt drops to 22%. The 8% drift exceeds the 5% tolerance band. The investor trims 8% of equity gains and shifts into liquid debt, locking in equity profits at high valuations.",
                takeaway="Systematic rebalancing forces you to take profits at market peaks without emotional greed.",
            )
        ],
        important_notes=[
            "Factor in Indian LTCG (Long-Term Capital Gains) and STCG tax rates before initiating portfolio changes.",
        ],
        common_mistakes=[
            "Constantly chasing whichever sector was the top performer of the previous year.",
        ],
        limitations=[
            "Premature rebalancing in a prolonged structural multi-year bull market can slightly dilute maximum upside.",
        ],
        illustration_key="sector_rotation_clock",
        prev_lesson_id="lesson-asset-allocation",
        next_lesson_id=None,
    ),
]


# =====================================================================
# QUIZZES DATA (Internal with Answer Keys & Explanations)
# =====================================================================

QUIZZES_DATA: Dict[str, Dict[str, Any]] = {
    "quiz-lesson-nse-bse-structure": {
        "lesson_id": "lesson-nse-bse-structure",
        "title": "Knowledge Check: NSE, BSE & Market Structure",
        "passing_score": 70,
        "questions": [
            QuizQuestionInternal(
                id="q-nse-1",
                question="What are the standard regular continuous trading hours on NSE and BSE for equity cash markets (IST)?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    QuizOption(id="opt-a", text="09:00 AM to 03:00 PM"),
                    QuizOption(id="opt-b", text="09:15 AM to 03:30 PM"),
                    QuizOption(id="opt-c", text="09:30 AM to 04:00 PM"),
                    QuizOption(id="opt-d", text="10:00 AM to 03:30 PM"),
                ],
                correct_option_id="opt-b",
                explanation="In India, normal continuous market trading hours run from 09:15 AM to 03:30 PM IST, preceded by the pre-open session from 09:00 to 09:08 AM.",
            ),
            QuizQuestionInternal(
                id="q-nse-2",
                question="The pre-open session between 09:00 AM and 09:08 AM IST is designed to discover an equilibrium opening price without chaotic execution.",
                question_type=QuestionType.TRUE_FALSE,
                options=[
                    QuizOption(id="opt-true", text="True"),
                    QuizOption(id="opt-false", text="False"),
                ],
                correct_option_id="opt-true",
                explanation="True. The pre-open auction collects orders to calculate a single equilibrium price, stabilizing market opens against overnight news.",
            ),
            QuizQuestionInternal(
                id="q-nse-3",
                question="Which regulatory authority is responsible for governing and protecting investor rights in Indian securities markets?",
                question_type=QuestionType.CONCEPT_IDENTIFY,
                options=[
                    QuizOption(id="opt-a", text="RBI (Reserve Bank of India)"),
                    QuizOption(id="opt-b", text="SEBI (Securities and Exchange Board of India)"),
                    QuizOption(id="opt-c", text="IRDAI"),
                    QuizOption(id="opt-d", text="NITI Aayog"),
                ],
                correct_option_id="opt-b",
                explanation="SEBI is the primary statutory regulator of securities and commodity markets in India.",
            ),
        ],
    },

    "quiz-lesson-order-types": {
        "lesson_id": "lesson-order-types",
        "title": "Knowledge Check: Order Types & Execution",
        "passing_score": 70,
        "questions": [
            QuizQuestionInternal(
                id="q-ord-1",
                question="Which type of order guarantees immediate execution but does not guarantee the execution price?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    QuizOption(id="opt-a", text="Limit Order"),
                    QuizOption(id="opt-b", text="Market Order"),
                    QuizOption(id="opt-c", text="Stop-Loss Limit Order"),
                    QuizOption(id="opt-d", text="Good-Till-Cancelled Order"),
                ],
                correct_option_id="opt-b",
                explanation="A Market Order executes instantly at the best prevailing price in the order book, which can result in slippage if liquidity is thin.",
            ),
            QuizQuestionInternal(
                id="q-ord-2",
                question="In a Stop-Loss Limit (SL-L) order, what role does the 'Trigger Price' play?",
                question_type=QuestionType.CONCEPT_IDENTIFY,
                options=[
                    QuizOption(id="opt-a", text="It is the exact price your order must execute at."),
                    QuizOption(id="opt-b", text="It is the benchmark price that activates the order and sends it to the exchange order book."),
                    QuizOption(id="opt-c", text="It defines your profit target."),
                    QuizOption(id="opt-d", text="It cancels your order if not filled in 5 minutes."),
                ],
                correct_option_id="opt-b",
                explanation="The trigger price is the threshold that, when breached, activates your order and places it into the exchange matching engine.",
            ),
            QuizQuestionInternal(
                id="q-ord-3",
                question="Scenario: You own shares trading at ₹500 and want to buy more, but only if the price pulls back to ₹480 or cheaper. Which order type should you place?",
                question_type=QuestionType.SCENARIO_BASED,
                scenario_context="Current market price is ₹500. Target purchase price is ₹480.",
                options=[
                    QuizOption(id="opt-a", text="Market Order"),
                    QuizOption(id="opt-b", text="Buy Limit Order at ₹480"),
                    QuizOption(id="opt-c", text="Stop-Loss Market Order at ₹510"),
                    QuizOption(id="opt-d", text="Immediate-or-Cancel Order"),
                ],
                correct_option_id="opt-b",
                explanation="A Buy Limit Order at ₹480 guarantees you will only pay ₹480 or less, and will not execute while the price remains at ₹500.",
            ),
        ],
    },

    "quiz-lesson-candle-anatomy-doji": {
        "lesson_id": "lesson-candle-anatomy-doji",
        "title": "Knowledge Check: Candlestick Anatomy & Dojis",
        "passing_score": 70,
        "questions": [
            QuizQuestionInternal(
                id="q-doji-1",
                question="What visual characteristic defines a Doji candlestick?",
                question_type=QuestionType.CANDLESTICK_IDENTIFY,
                options=[
                    QuizOption(id="opt-a", text="A very tall green body with zero shadows"),
                    QuizOption(id="opt-b", text="An opening price and closing price that are virtually identical, resulting in a thin horizontal line body"),
                    QuizOption(id="opt-c", text="A body three times the length of the lower shadow"),
                    QuizOption(id="opt-d", text="Consecutive gaps above resistance"),
                ],
                correct_option_id="opt-b",
                explanation="A Doji represents market equilibrium where open and close are nearly identical, indicating indecision between buyers and sellers.",
            ),
            QuizQuestionInternal(
                id="q-doji-2",
                question="A Dragonfly Doji has a long lower shadow and virtually no upper shadow. What does this indicate about session price action?",
                question_type=QuestionType.CANDLESTICK_IDENTIFY,
                options=[
                    QuizOption(id="opt-a", text="Bears aggressively maintained control into the close."),
                    QuizOption(id="opt-b", text="Sellers pushed prices sharply down during the session, but buyers completely rejected the lows and pushed price back to the open."),
                    QuizOption(id="opt-c", text="Volume was completely absent throughout the day."),
                    QuizOption(id="opt-d", text="The exchange halted trading due to circuit limits."),
                ],
                correct_option_id="opt-b",
                explanation="The long lower wick of a Dragonfly Doji proves that aggressive institutional buyers rejected lower prices and brought price back to the session high.",
            ),
            QuizQuestionInternal(
                id="q-doji-3",
                question="A Doji alone guarantees that an ongoing trend will immediately reverse.",
                question_type=QuestionType.TRUE_FALSE,
                options=[
                    QuizOption(id="opt-true", text="True"),
                    QuizOption(id="opt-false", text="False"),
                ],
                correct_option_id="opt-false",
                explanation="False. A Doji reflects indecision or a temporary pause. It requires context and confirmation from subsequent candles before signaling a reversal.",
            ),
        ],
    },

    "quiz-lesson-hammer-shooting-star": {
        "lesson_id": "lesson-hammer-shooting-star",
        "title": "Knowledge Check: Hammer & Shooting Star",
        "passing_score": 70,
        "questions": [
            QuizQuestionInternal(
                id="q-ham-1",
                question="To qualify as a valid Hammer pattern, what must the relationship between the lower shadow and the real body be?",
                question_type=QuestionType.CANDLESTICK_IDENTIFY,
                options=[
                    QuizOption(id="opt-a", text="Lower shadow must be shorter than the body."),
                    QuizOption(id="opt-b", text="Lower shadow must be at least twice (2x) the height of the real body, with little to no upper shadow."),
                    QuizOption(id="opt-c", text="Upper shadow must be twice the lower shadow."),
                    QuizOption(id="opt-d", text="The body must be red and engulf the previous 3 candles."),
                ],
                correct_option_id="opt-b",
                explanation="A true Hammer requires a small real body at the top of the range and a long lower shadow at least 2 times the body length.",
            ),
            QuizQuestionInternal(
                id="q-ham-2",
                question="A Shooting Star appears at the top of an uptrend with a long upper shadow. What psychological signal does it convey?",
                question_type=QuestionType.CONCEPT_IDENTIFY,
                options=[
                    QuizOption(id="opt-a", text="Buyers successfully broke all overhead resistance."),
                    QuizOption(id="opt-b", text="Bulls tried to push prices higher, but were decisively overwhelmed by sellers who drove price back near the open."),
                    QuizOption(id="opt-c", text="The trend will continue upwards indefinitely."),
                    QuizOption(id="opt-d", text="Volume dried up completely."),
                ],
                correct_option_id="opt-b",
                explanation="The long upper shadow on a Shooting Star demonstrates that buyers were exhausted and rejected by sellers at new highs.",
            ),
            QuizQuestionInternal(
                id="q-ham-3",
                question="Scenario: A candle with a small body and a long lower wick appears after an extended 10-day rally. What pattern is this?",
                question_type=QuestionType.SCENARIO_BASED,
                scenario_context="Formed after an uptrend at swing high resistance.",
                options=[
                    QuizOption(id="opt-a", text="Hammer"),
                    QuizOption(id="opt-b", text="Hanging Man"),
                    QuizOption(id="opt-c", text="Inverted Hammer"),
                    QuizOption(id="opt-d", text="Morning Star"),
                ],
                correct_option_id="opt-b",
                explanation="When this anatomy appears at the top of an uptrend rather than after a downtrend, it is classified as a Hanging Man, a potential bearish warning.",
            ),
        ],
    },

    "quiz-lesson-engulfing-patterns": {
        "lesson_id": "lesson-engulfing-patterns",
        "title": "Knowledge Check: Engulfing Patterns",
        "passing_score": 70,
        "questions": [
            QuizQuestionInternal(
                id="q-eng-1",
                question="In a classic Bullish Engulfing setup, which candle is larger?",
                question_type=QuestionType.CANDLESTICK_IDENTIFY,
                options=[
                    QuizOption(id="opt-a", text="The first red candle"),
                    QuizOption(id="opt-b", text="The second green candle whose real body completely covers the first candle's body"),
                    QuizOption(id="opt-c", text="Both candles are identical in size"),
                    QuizOption(id="opt-d", text="The third confirmation candle"),
                ],
                correct_option_id="opt-b",
                explanation="The defining feature of a Bullish Engulfing pattern is that Candle 2's green real body completely engulfs the preceding red candle's body.",
            ),
            QuizQuestionInternal(
                id="q-eng-2",
                question="Engulfing patterns have higher statistical reliability when supported by which accompanying factor?",
                question_type=QuestionType.CONCEPT_IDENTIFY,
                options=[
                    QuizOption(id="opt-a", text="Below-average trading volume"),
                    QuizOption(id="opt-b", text="Expansion in trading volume on the engulfing candle at a verified support or resistance zone"),
                    QuizOption(id="opt-c", text="A narrow sideways consolidation"),
                    QuizOption(id="opt-d", text="Immediate gap openings in the opposite direction"),
                ],
                correct_option_id="opt-b",
                explanation="High volume confirmation demonstrates institutional commitment to the trend change.",
            ),
        ],
    },

    "quiz-lesson-rsi-indicator": {
        "lesson_id": "lesson-rsi-indicator",
        "title": "Knowledge Check: RSI Momentum & Divergences",
        "passing_score": 70,
        "questions": [
            QuizQuestionInternal(
                id="q-rsi-1",
                question="What is the standard lookback period originally specified by J. Welles Wilder for the RSI indicator?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    QuizOption(id="opt-a", text="7 periods"),
                    QuizOption(id="opt-b", text="14 periods"),
                    QuizOption(id="opt-c", text="21 periods"),
                    QuizOption(id="opt-d", text="50 periods"),
                ],
                correct_option_id="opt-b",
                explanation="The standard and universally used default setting for RSI is 14 periods.",
            ),
            QuizQuestionInternal(
                id="q-rsi-2",
                question="Scenario: NIFTY makes a Higher High on the price chart, but RSI creates a Lower High. What does this divergence signal?",
                question_type=QuestionType.SCENARIO_BASED,
                scenario_context="Price = Higher High; RSI = Lower High.",
                options=[
                    QuizOption(id="opt-a", text="Regular Bullish Divergence; expect instant rally"),
                    QuizOption(id="opt-b", text="Regular Bearish Divergence; warning that upward buying momentum is waning"),
                    QuizOption(id="opt-c", text="Hidden Bullish Divergence; buy aggressively"),
                    QuizOption(id="opt-d", text="Zero divergence; completely normal behavior"),
                ],
                correct_option_id="opt-b",
                explanation="When price climbs to higher peaks while momentum fails to match and prints a lower peak, it forms a Regular Bearish Divergence.",
            ),
            QuizQuestionInternal(
                id="q-rsi-3",
                question="In a powerful bull market, an RSI reading above 70 means you should immediately short the stock because it is guaranteed to drop.",
                question_type=QuestionType.TRUE_FALSE,
                options=[
                    QuizOption(id="opt-true", text="True"),
                    QuizOption(id="opt-false", text="False"),
                ],
                correct_option_id="opt-false",
                explanation="False. In strong momentum trends, RSI can stay 'overbought' (>70) for weeks as price continues to multiply. Shorting purely on RSI > 70 is a severe beginner pitfall.",
            ),
        ],
    },

    "quiz-lesson-one-percent-rule": {
        "lesson_id": "lesson-one-percent-rule",
        "title": "Knowledge Check: Risk Management & 1% Rule",
        "passing_score": 70,
        "questions": [
            QuizQuestionInternal(
                id="q-risk-1",
                question="If your total trading account capital is ₹4,00,000, what is the maximum rupee loss you should allow on a single trade under the 1% rule?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    QuizOption(id="opt-a", text="₹40,000"),
                    QuizOption(id="opt-b", text="₹4,000"),
                    QuizOption(id="opt-c", text="₹400"),
                    QuizOption(id="opt-d", text="₹10,000"),
                ],
                correct_option_id="opt-b",
                explanation="1% of ₹4,00,000 is strictly ₹4,000. Under no circumstances should your stop-loss exceed this monetary amount.",
            ),
            QuizQuestionInternal(
                id="q-risk-2",
                question="Scenario: Account capital is ₹1,00,000 (1% risk = ₹1,000). You buy Stock ABC at ₹200 with a stop-loss at ₹190. What is your correct position size?",
                question_type=QuestionType.SCENARIO_BASED,
                scenario_context="Account: ₹1,00,000. Risk per share: ₹200 - ₹190 = ₹10. Total risk: ₹1,000.",
                options=[
                    QuizOption(id="opt-a", text="500 shares"),
                    QuizOption(id="opt-b", text="100 shares"),
                    QuizOption(id="opt-c", text="1,000 shares"),
                    QuizOption(id="opt-d", text="50 shares"),
                ],
                correct_option_id="opt-b",
                explanation="Position Size = Allowed Risk (₹1,000) / Risk Per Share (₹10) = 100 shares. Total invested = ₹20,000. If stopped out at ₹190, loss is exactly ₹1,000.",
            ),
            QuizQuestionInternal(
                id="q-risk-3",
                question="Why is an asymmetric recovery curve dangerous if you risk 10% or more per trade?",
                question_type=QuestionType.CONCEPT_IDENTIFY,
                options=[
                    QuizOption(id="opt-a", text="Because brokers charge higher commissions on losses."),
                    QuizOption(id="opt-b", text="Because as capital drops, the percentage gain required to return to breakeven expands geometrically (e.g. 50% loss requires 100% gain)."),
                    QuizOption(id="opt-c", text="Because trading hours are reduced during drawdowns."),
                    QuizOption(id="opt-d", text="Because SEBI limits order placement after losses."),
                ],
                correct_option_id="opt-b",
                explanation="Capital destruction is mathematically asymmetric: losing 50% of your account requires a 100% gain on the remaining funds just to get back to zero.",
            ),
        ],
    },

    "quiz-lesson-risk-reward-expectancy": {
        "lesson_id": "lesson-risk-reward-expectancy",
        "title": "Knowledge Check: Expectancy & R:R",
        "passing_score": 70,
        "questions": [
            QuizQuestionInternal(
                id="q-rr-1",
                question="If a trader maintains a strict 1:2 Risk-to-Reward ratio, what minimum win rate is needed just to break even (excluding fees)?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    QuizOption(id="opt-a", text="50%"),
                    QuizOption(id="opt-b", text="33.3%"),
                    QuizOption(id="opt-c", text="66.7%"),
                    QuizOption(id="opt-d", text="25%"),
                ],
                correct_option_id="opt-b",
                explanation="With 1:2 R:R, winning 1 trade (+2R) offsets 2 losing trades (-1R + -1R = -2R). Thus, a 33.3% win rate breaks even.",
            ),
            QuizQuestionInternal(
                id="q-rr-2",
                question="A trader with an 85% win rate is guaranteed to be more profitable than a trader with a 40% win rate.",
                question_type=QuestionType.TRUE_FALSE,
                options=[
                    QuizOption(id="opt-true", text="True"),
                    QuizOption(id="opt-false", text="False"),
                ],
                correct_option_id="opt-false",
                explanation="False. If the 85% trader takes small profits (+₹500) and lets the 15% losses run uncontrollably (-₹10,000), they will be severely unprofitable compared to a disciplined 1:3 R:R trader with a 40% win rate.",
            ),
        ],
    },
}
