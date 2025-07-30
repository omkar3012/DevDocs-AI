"""
Spark Analytics for DevDocs AI
Processes query logs and generates insights about usage patterns
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os

def create_spark_session():
    """Create Spark session with necessary configurations"""
    return SparkSession.builder \
        .appName("DevDocs AI Analytics") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def analyze_query_patterns(spark, query_logs_df):
    """Analyze query patterns and generate insights"""
    
    # Most common queries
    common_queries = query_logs_df \
        .groupBy("query") \
        .count() \
        .orderBy(col("count").desc()) \
        .limit(10)
    
    # Average response time by document
    avg_response_time = query_logs_df \
        .groupBy("doc_id") \
        .agg(
            avg("response_time_ms").alias("avg_response_time"),
            count("*").alias("query_count")
        ) \
        .orderBy(col("query_count").desc())
    
    # Query volume over time
    query_volume = query_logs_df \
        .withColumn("date", date_format("timestamp", "yyyy-MM-dd")) \
        .groupBy("date") \
        .count() \
        .orderBy("date")
    
    return {
        "common_queries": common_queries,
        "avg_response_time": avg_response_time,
        "query_volume": query_volume
    }

def analyze_feedback(spark, feedback_df):
    """Analyze user feedback patterns"""
    
    # Overall feedback distribution
    feedback_distribution = feedback_df \
        .groupBy("was_helpful") \
        .count()
    
    # Feedback by document
    feedback_by_doc = feedback_df \
        .groupBy("doc_id") \
        .agg(
            sum(when(col("was_helpful") == True, 1).otherwise(0)).alias("helpful_count"),
            sum(when(col("was_helpful") == False, 1).otherwise(0)).alias("unhelpful_count"),
            count("*").alias("total_feedback")
        ) \
        .withColumn("helpful_rate", col("helpful_count") / col("total_feedback"))
    
    return {
        "feedback_distribution": feedback_distribution,
        "feedback_by_doc": feedback_by_doc
    }

def generate_recommendations(spark, query_logs_df, feedback_df):
    """Generate recommendations based on analytics"""
    
    # Find documents with low query count (potentially stale)
    stale_docs = query_logs_df \
        .groupBy("doc_id") \
        .count() \
        .filter(col("count") < 5) \
        .orderBy("count")
    
    # Find queries with low helpfulness rate
    problematic_queries = feedback_df \
        .groupBy("query") \
        .agg(
            sum(when(col("was_helpful") == True, 1).otherwise(0)).alias("helpful_count"),
            count("*").alias("total_feedback")
        ) \
        .withColumn("helpful_rate", col("helpful_count") / col("total_feedback")) \
        .filter(col("helpful_rate") < 0.5) \
        .orderBy("helpful_rate")
    
    return {
        "stale_documents": stale_docs,
        "problematic_queries": problematic_queries
    }

def main():
    """Main analytics pipeline"""
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Read data from Kafka or database
        # For this example, we'll assume data is available as DataFrames
        
        # Analyze query patterns
        query_insights = analyze_query_patterns(spark, query_logs_df)
        
        # Analyze feedback
        feedback_insights = analyze_feedback(spark, feedback_df)
        
        # Generate recommendations
        recommendations = generate_recommendations(spark, query_logs_df, feedback_df)
        
        # Save results
        query_insights["common_queries"].write.mode("overwrite").parquet("analytics/common_queries")
        query_insights["avg_response_time"].write.mode("overwrite").parquet("analytics/avg_response_time")
        query_insights["query_volume"].write.mode("overwrite").parquet("analytics/query_volume")
        
        feedback_insights["feedback_distribution"].write.mode("overwrite").parquet("analytics/feedback_distribution")
        feedback_insights["feedback_by_doc"].write.mode("overwrite").parquet("analytics/feedback_by_doc")
        
        recommendations["stale_documents"].write.mode("overwrite").parquet("analytics/stale_documents")
        recommendations["problematic_queries"].write.mode("overwrite").parquet("analytics/problematic_queries")
        
        print("✅ Analytics completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in analytics pipeline: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main() 