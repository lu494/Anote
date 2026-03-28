from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

def setup_password_change(app, db, User, login_required, json_response):
    @app.route('/user/changePassword', methods=['POST'])
    @login_required
    def change_password(current_user):
        data = request.get_json(silent=True) or {}
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')
        if not old_password:
            return json_response(4003, '旧密码不能为空', status=400)
        if not new_password:
            return json_response(4003, '新密码不能为空', status=400)
        if len(new_password) < 6:
            return json_response(4003, '新密码长度至少为6位', status=400)
        if old_password == new_password:
            return json_response(4003, '新密码不能与旧密码相同', status=400)
        if not current_user.check_password(old_password):
            return json_response(4003, '旧密码错误', status=400)
        current_user.set_password(new_password)
        db.session.commit()
        return json_response(0, '密码修改成功')
