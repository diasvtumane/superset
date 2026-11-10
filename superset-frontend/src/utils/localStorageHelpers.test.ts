/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import {
  getItem,
  setItem,
  LocalStorageKeys,
  getUserThumbnailPreference,
  setUserThumbnailPreference,
} from 'src/utils/localStorageHelpers';

// eslint-disable-next-line no-restricted-globals -- TODO: Migrate from describe blocks
describe('localStorageHelpers', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterAll(() => {
    localStorage.clear();
  });

  test('gets a value that was set', () => {
    setItem(LocalStorageKeys.IsDatapanelOpen, false);

    expect(getItem(LocalStorageKeys.IsDatapanelOpen, true)).toBe(false);
  });

  test('returns the default value for an unset value', () => {
    expect(getItem(LocalStorageKeys.IsDatapanelOpen, true)).toBe(true);
  });
});

test('getUserThumbnailPreference returns undefined when no preference exists', () => {
  localStorage.clear();
  expect(getUserThumbnailPreference('42')).toBeUndefined();
});

test('setUserThumbnailPreference stores and getUserThumbnailPreference reads the namespaced key', () => {
  localStorage.clear();
  setUserThumbnailPreference('42', false);
  expect(getUserThumbnailPreference('42')).toBe(false);

  setUserThumbnailPreference('42', true);
  expect(getUserThumbnailPreference('42')).toBe(true);
});

test('getUserThumbnailPreference falls back to legacy bare user-id key', () => {
  localStorage.clear();
  localStorage.setItem('7', JSON.stringify({ thumbnails: false }));
  expect(getUserThumbnailPreference('7')).toBe(false);
});

test('getUserThumbnailPreference migrates legacy value to the namespaced key', () => {
  localStorage.clear();
  localStorage.setItem('7', JSON.stringify({ thumbnails: true }));

  getUserThumbnailPreference('7');

  const stored = JSON.parse(
    localStorage.getItem(
      LocalStorageKeys.HomepageUserThumbnailPreference,
    ) as string,
  );
  expect(stored['7']).toBe(true);
});

test('getUserThumbnailPreference prefers the namespaced key over the legacy key', () => {
  localStorage.clear();
  localStorage.setItem('7', JSON.stringify({ thumbnails: false }));
  setUserThumbnailPreference('7', true);

  expect(getUserThumbnailPreference('7')).toBe(true);
});

test('setUserThumbnailPreference keeps preferences for other users intact', () => {
  localStorage.clear();
  setUserThumbnailPreference('1', true);
  setUserThumbnailPreference('2', false);

  expect(getUserThumbnailPreference('1')).toBe(true);
  expect(getUserThumbnailPreference('2')).toBe(false);
});
