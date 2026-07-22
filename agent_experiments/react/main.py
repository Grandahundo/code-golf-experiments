def solve_task(task_id, task_data, model, max_rounds=30):
    messages = [system_prompt, user_prompt(task_id, task_data["train"])]
    
    best_code = None
    best_bytes = float('inf')
    history = []
    
    for round in range(1, max_rounds + 1):
        # 1. 模型输出
        response = model.generate(messages)
        code = extract_code(response)
        
        # 2. 提交判题
        result = submit_code(code, task_data["test"])
        
        # 3. 更新最优
        if result["status"] == "AC" and result["bytes"] < best_bytes:
            best_bytes = result["bytes"]
            best_code = code
        
        # 4. 记录
        history.append({
            "round": round,
            "code": code,
            "status": result["status"],
            "bytes": result.get("bytes"),
            "message": result.get("message")
        })
        
        # 5. 追加到上下文
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": 
            f"Result: {result['status']}. " +
            (f"Bytes: {result['bytes']}. Current best: {best_bytes}B." if result["status"]=="AC" 
             else f"Error: {result['message']}. Current best: {best_bytes if best_code else 'none'}B.")
        })
    
    # 6. 返回
    return {
        "solved": best_code is not None,
        "bytes": best_bytes if best_code else None,
        "code": best_code,
        "rounds": max_rounds,
        "history": history
    }