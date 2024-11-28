# if reader['function'] is not None:  # если производится приёмка/отгрузка баллонов
#     batch_data = await balloon_api.get_batch_balloons(reader['function'])
#
#     if batch_data:  # если партия активна - добавляем в неё пройденный баллон
#         reader['batch']['batch_id'] = batch_data['id']
#         reader['batch']['balloon_id'] = balloon_passport['id']
#         await balloon_api.add_balloon_to_batch(reader)
